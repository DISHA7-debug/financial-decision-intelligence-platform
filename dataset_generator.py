import csv
import json
import os
from datetime import datetime
from typing import Any

from state import AgentState
from nodes.node1_ingest import run_ingestion_from_text
from nodes.node2_risk import run_risk_analysis
from nodes.node3_rag import run_retrieval
from nodes.node4_rules import run_rule_decision
from utils.sec_downloader import download_latest_10k
from utils.sec_parser import load_raw_filing
from utils.xbrl_parser import extract_financial_data_xbrl

UNIVERSE_PATH = (
    "data/companies/training_universe.json"
)

FEATURE_COLUMNS = [
    "company",
    "revenue",
    "previous_revenue",
    "revenue_growth",
    "net_income",
    "current_ratio",
    "debt_ratio",
    "gross_margin",
    "asset_turnover",
    "altman_z",
    "piotroski_f",
    "recommendation",
]

DATASET_PATH = (
    "data/datasets/company_features.csv"
)

FAILURES_PATH = (
    "data/datasets/failed_companies.log"
)

CRITICAL_FIELDS = (
    "revenue",
    "total_liabilities",
    "total_assets",
    "net_income",
)


def load_training_universe(
    universe_path: str = UNIVERSE_PATH,
) -> list[dict[str, str]]:
    with open(universe_path, "r") as universe_file:
        return json.load(universe_file)


def _load_filing_for_ticker(
    ticker: str
) -> str:
    base_path = (
        f"data/sec_filings/sec-edgar-filings/"
        f"{ticker}/10-K"
    )

    if not os.path.exists(base_path):
        print(
            f"\nDownloading filing for {ticker}...\n"
        )
        download_latest_10k(ticker)

    folders = sorted(
        os.listdir(base_path)
    )
    latest_folder = folders[-1]
    filing_path = os.path.join(
        base_path,
        latest_folder,
        "full-submission.txt",
    )

    return load_raw_filing(filing_path)


def _ensure_valid_cache(
    cache_key: str,
    filing_text: str,
) -> None:
    cache_file = (
        f"data/cache/{cache_key}.json"
    )

    if not os.path.exists(cache_file):
        return

    fresh = extract_financial_data_xbrl(filing_text)

    with open(cache_file, "r") as cache_handle:
        cached_data = json.load(cache_handle)

    current_year = cached_data.get("current_year", {})

    for field in CRITICAL_FIELDS:
        cached_value = current_year.get(field)
        fresh_value = getattr(
            fresh.current_year,
            field,
        )

        if cached_value is None and fresh_value is not None:
            os.remove(cache_file)
            return

    if (
        current_year.get("revenue")
        != fresh.current_year.revenue
    ):
        os.remove(cache_file)


def run_company_pipeline(
    company_name: str,
    ticker: str,
) -> AgentState:
    cache_key = f"{ticker.lower()}_sec"
    filing_text = _load_filing_for_ticker(ticker)
    _ensure_valid_cache(cache_key, filing_text)

    financial_data = run_ingestion_from_text(
        filing_text,
        cache_key,
    )

    state = AgentState(
        company_name=company_name,
        financial_data=financial_data,
    )

    state = run_risk_analysis(state)
    state = run_retrieval(
        state,
        "major business risks",
    )
    state = run_rule_decision(state)

    return state


def _safe_ratio(
    numerator: float | None,
    denominator: float | None,
) -> float | None:
    if (
        numerator is None
        or denominator is None
        or denominator == 0
    ):
        return None

    return numerator / denominator


def _extract_features(
    state: AgentState
) -> dict[str, Any]:
    financials = state.financial_data
    current = financials.current_year
    previous = financials.previous_year

    revenue = current.revenue
    previous_revenue = previous.revenue

    revenue_growth = None

    if (
        revenue is not None
        and previous_revenue is not None
        and previous_revenue != 0
    ):
        revenue_growth = (
            (revenue - previous_revenue)
            / previous_revenue
        )

    return {
        "company": state.company_name,
        "revenue": revenue,
        "previous_revenue": previous_revenue,
        "revenue_growth": revenue_growth,
        "net_income": current.net_income,
        "current_ratio": _safe_ratio(
            current.current_assets,
            current.current_liabilities,
        ),
        "debt_ratio": _safe_ratio(
            current.total_liabilities,
            current.total_assets,
        ),
        "gross_margin": _safe_ratio(
            current.gross_profit,
            revenue,
        ),
        "asset_turnover": _safe_ratio(
            revenue,
            current.total_assets,
        ),
        "altman_z": (
            state.risk_metrics.altman_z_score
            if state.risk_metrics
            else None
        ),
        "piotroski_f": (
            state.risk_metrics.piotroski_f_score
            if state.risk_metrics
            else None
        ),
        "recommendation": (
            state.decision_output.recommendation
            if state.decision_output
            else None
        ),
    }


def _is_complete_row(
    row: dict[str, Any]
) -> bool:
    return (
        row.get("revenue") is not None
        and row.get("altman_z") is not None
        and row.get("piotroski_f") is not None
        and row.get("recommendation") is not None
    )


def _format_csv_value(
    value: Any
) -> str:
    if value is None:
        return ""

    if isinstance(value, float):
        return f"{value:.6f}"

    return str(value)


def _log_failure(
    company_name: str,
    ticker: str,
    error: Exception,
    failures_path: str = FAILURES_PATH,
) -> None:
    os.makedirs(
        os.path.dirname(failures_path),
        exist_ok=True,
    )

    timestamp = datetime.now().isoformat(
        timespec="seconds"
    )

    with open(failures_path, "a") as failures_file:
        failures_file.write(
            f"{timestamp}\t{company_name}\t{ticker}\t{error}\n"
        )


def generate_dataset(
    companies: list[dict[str, str]] | None = None,
    output_path: str = DATASET_PATH,
    failures_path: str = FAILURES_PATH,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    if companies is None:
        companies = load_training_universe()

    if os.path.exists(failures_path):
        os.remove(failures_path)

    rows: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []

    for entry in companies:
        company_name = entry["company"]
        ticker = entry["ticker"]

        print(
            f"\nProcessing {company_name} ({ticker})...\n"
        )

        try:
            state = run_company_pipeline(
                company_name,
                ticker,
            )
            row = _extract_features(state)

            if not _is_complete_row(row):
                raise ValueError(
                    "Incomplete feature row after pipeline"
                )

            rows.append(row)
        except Exception as error:
            print(
                f"Failed to process {company_name}: {error}\n"
            )
            _log_failure(
                company_name,
                ticker,
                error,
                failures_path,
            )
            failures.append({
                "company": company_name,
                "ticker": ticker,
                "error": str(error),
            })

    output_dir = os.path.dirname(output_path)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=FEATURE_COLUMNS,
        )
        writer.writeheader()

        for row in rows:
            writer.writerow({
                column: _format_csv_value(row.get(column))
                for column in FEATURE_COLUMNS
            })

    return rows, failures


def print_dataset_summary(
    rows: list[dict[str, Any]],
    failures: list[dict[str, str]],
    output_path: str = DATASET_PATH,
    failures_path: str = FAILURES_PATH,
) -> None:
    recommendation_counts: dict[str, int] = {}

    for row in rows:
        recommendation = row.get("recommendation") or "UNKNOWN"
        recommendation_counts[recommendation] = (
            recommendation_counts.get(recommendation, 0) + 1
        )

    print("\n===== DATASET SUMMARY =====\n")
    print(f"Output file: {output_path}")
    print(f"Successful rows: {len(rows)}")
    print(f"Failed companies: {len(failures)}")
    print(f"Failure log: {failures_path}")
    print(f"Columns: {', '.join(FEATURE_COLUMNS)}")
    print("\nRecommendations:")

    for recommendation, count in sorted(
        recommendation_counts.items()
    ):
        print(f"  {recommendation}: {count}")

    if failures:
        print("\nFailures:")

        for failure in failures:
            print(
                f"  {failure['company']} ({failure['ticker']}): "
                f"{failure['error']}"
            )

    print("\nSample rows:\n")

    for row in rows[:10]:
        print(
            f"{row['company']}: "
            f"revenue={row.get('revenue')}, "
            f"altman_z={row.get('altman_z')}, "
            f"piotroski_f={row.get('piotroski_f')}, "
            f"recommendation={row.get('recommendation')}"
        )


if __name__ == "__main__":
    dataset_rows, dataset_failures = generate_dataset()
    print_dataset_summary(
        dataset_rows,
        dataset_failures,
    )
