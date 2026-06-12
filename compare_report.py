import os
import sys
from dataclasses import dataclass, field
from datetime import datetime

# macOS Apple Silicon: PyTorch (RAG) and XGBoost both link libomp.
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")

from ml.predict_xgboost import predict_recommendation
from risk_intelligence import extract_identified_risks
from workflow import run_workflow

REPORT_PATH = "reports/investment_committee_report.txt"

RECOMMENDATION_RANK = {
    "BUY": 3,
    "HOLD": 2,
    "AVOID": 1,
    "ERROR": 0,
    "UNAVAILABLE": 0,
}

RISK_CLASS_RANK = {
    "Distress Zone": 0,
    "Grey Zone": 1,
    "Gray Zone": 1,
    "Safe Zone": 2,
}


@dataclass
class CompanySnapshot:
    company: str
    revenue: float | None = None
    revenue_growth: float | None = None
    net_income: float | None = None
    current_ratio: float | None = None
    debt_ratio: float | None = None
    altman_z: float | None = None
    piotroski_f: int | None = None
    risk_classification: str | None = None
    rule_recommendation: str | None = None
    ml_recommendation: str | None = None
    ml_confidence: str | None = None
    identified_risks: list = field(default_factory=list)
    rank: int | None = None
    error: str | None = None


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


def _format_millions(value: float | None) -> str:
    if value is None:
        return "N/A"

    return f"${value:,.0f}M"


def _format_percent(value: float | None) -> str:
    if value is None:
        return "N/A"

    return f"{value * 100:.1f}%"


def _format_ratio(value: float | None) -> str:
    if value is None:
        return "N/A"

    return f"{value:.2f}"


def collect_company_snapshot(
    company_name: str,
) -> CompanySnapshot:
    try:
        state = run_workflow(company_name)
        ml_prediction = predict_recommendation(state)
    except Exception as error:
        return CompanySnapshot(
            company=company_name,
            error=str(error),
            rule_recommendation="ERROR",
            ml_recommendation="ERROR",
        )

    financials = state.financial_data
    risk = state.risk_metrics
    decision = state.decision_output

    current = (
        financials.current_year
        if financials
        else None
    )
    previous = (
        financials.previous_year
        if financials
        else None
    )

    revenue = current.revenue if current else None
    previous_revenue = (
        previous.revenue if previous else None
    )

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

    return CompanySnapshot(
        company=company_name,
        revenue=revenue,
        revenue_growth=revenue_growth,
        net_income=(
            current.net_income if current else None
        ),
        current_ratio=_safe_ratio(
            current.current_assets if current else None,
            current.current_liabilities if current else None,
        ),
        debt_ratio=_safe_ratio(
            current.total_liabilities if current else None,
            current.total_assets if current else None,
        ),
        altman_z=(
            risk.altman_z_score if risk else None
        ),
        piotroski_f=(
            risk.piotroski_f_score if risk else None
        ),
        risk_classification=(
            risk.risk_classification if risk else None
        ),
        rule_recommendation=(
            decision.recommendation if decision else None
        ),
        ml_recommendation=ml_prediction.recommendation,
        ml_confidence=ml_prediction.confidence,
        identified_risks=extract_identified_risks(
            state.retrieved_context
        ),
    )


def rank_companies(
    snapshots: list[CompanySnapshot],
) -> list[CompanySnapshot]:
    ranked = sorted(
        snapshots,
        key=lambda row: (
            RECOMMENDATION_RANK.get(
                row.rule_recommendation or "",
                0,
            ),
            row.altman_z or 0.0,
            row.piotroski_f or 0,
        ),
        reverse=True,
    )

    for index, row in enumerate(ranked, start=1):
        row.rank = index

    return ranked


def _best_growth(
    snapshots: list[CompanySnapshot],
) -> CompanySnapshot | None:
    valid = [
        row
        for row in snapshots
        if row.revenue_growth is not None
    ]

    if not valid:
        return None

    return max(
        valid,
        key=lambda row: row.revenue_growth or 0.0,
    )


def _best_financial_health(
    snapshots: list[CompanySnapshot],
) -> CompanySnapshot | None:
    valid = [
        row
        for row in snapshots
        if row.altman_z is not None
        or row.piotroski_f is not None
    ]

    if not valid:
        return None

    return max(
        valid,
        key=lambda row: (
            row.altman_z or 0.0,
            row.piotroski_f or 0,
        ),
    )


def _highest_risk(
    snapshots: list[CompanySnapshot],
) -> CompanySnapshot | None:
    if not snapshots:
        return None

    return min(
        snapshots,
        key=lambda row: (
            RISK_CLASS_RANK.get(
                row.risk_classification or "",
                1,
            ),
            row.altman_z if row.altman_z is not None else 999.0,
            RECOMMENDATION_RANK.get(
                row.rule_recommendation or "",
                0,
            ),
            -(row.piotroski_f or 0),
        ),
    )


def _build_executive_summary(
    snapshots: list[CompanySnapshot],
) -> str:
    companies = ", ".join(row.company for row in snapshots)
    top = snapshots[0] if snapshots else None

    lines = [
        "This investment committee report consolidates due diligence across "
        f"{len(snapshots)} companies: {companies}.",
        "",
        "Each company was evaluated through the full agent pipeline: SEC "
        "ingestion, XBRL extraction, quantitative risk scoring, SEC risk "
        "retrieval, rule-based recommendation, and XGBoost ML prediction.",
    ]

    if top:
        lines.extend(
            [
                "",
                f"Top-ranked company: {top.company} "
                f"(rule: {top.rule_recommendation or 'N/A'}, "
                f"ML: {top.ml_recommendation or 'N/A'}).",
                f"Altman Z: {_format_ratio(top.altman_z)} | "
                f"Piotroski F: {top.piotroski_f if top.piotroski_f is not None else 'N/A'}.",
            ]
        )

    buy_count = sum(
        1
        for row in snapshots
        if row.rule_recommendation == "BUY"
    )
    hold_count = sum(
        1
        for row in snapshots
        if row.rule_recommendation == "HOLD"
    )
    avoid_count = sum(
        1
        for row in snapshots
        if row.rule_recommendation == "AVOID"
    )

    lines.extend(
        [
            "",
            "Rule-based distribution: "
            f"{buy_count} BUY, {hold_count} HOLD, {avoid_count} AVOID.",
        ]
    )

    return "\n".join(lines)


def _build_company_ranking(
    snapshots: list[CompanySnapshot],
) -> str:
    lines = [
        "Ranking methodology (descending priority):",
        "  1. Rule-based recommendation (BUY > HOLD > AVOID)",
        "  2. Altman Z-Score (higher = lower bankruptcy risk)",
        "  3. Piotroski F-Score (higher = stronger fundamentals)",
        "",
    ]

    for row in snapshots:
        lines.append(
            f"{row.rank}. {row.company} — "
            f"Rule: {row.rule_recommendation or 'N/A'} | "
            f"ML: {row.ml_recommendation or 'N/A'} | "
            f"Altman Z: {_format_ratio(row.altman_z)} | "
            f"Piotroski F: {row.piotroski_f if row.piotroski_f is not None else 'N/A'}"
        )

    return "\n".join(lines)


def _build_financial_table(
    snapshots: list[CompanySnapshot],
) -> str:
    headers = (
        "Company",
        "Revenue",
        "Rev Growth",
        "Net Income",
        "Current Ratio",
        "Debt Ratio",
        "Altman Z",
        "Piotroski F",
        "Risk Class",
        "Rule Rec",
        "ML Rec",
    )

    rows = [
        (
            row.company,
            _format_millions(row.revenue),
            _format_percent(row.revenue_growth),
            _format_millions(row.net_income),
            _format_ratio(row.current_ratio),
            _format_percent(row.debt_ratio),
            _format_ratio(row.altman_z),
            str(row.piotroski_f if row.piotroski_f is not None else "N/A"),
            row.risk_classification or "N/A",
            row.rule_recommendation or "N/A",
            row.ml_recommendation or "N/A",
        )
        for row in snapshots
    ]

    widths = [
        max(len(headers[i]), *(len(row[i]) for row in rows))
        for i in range(len(headers))
    ]

    header_line = " | ".join(
        headers[i].ljust(widths[i])
        for i in range(len(headers))
    )
    separator = "-+-".join("-" * widths[i] for i in range(len(headers)))
    body_lines = [
        " | ".join(
            row[i].ljust(widths[i])
            for i in range(len(headers))
        )
        for row in rows
    ]

    return "\n".join(
        [header_line, separator, *body_lines]
    )


def _build_best_growth(
    snapshots: list[CompanySnapshot],
) -> str:
    winner = _best_growth(snapshots)

    if winner is None:
        return "Insufficient revenue growth data across the universe."

    return (
        f"Best growth: {winner.company} "
        f"({_format_percent(winner.revenue_growth)} revenue growth, "
        f"revenue {_format_millions(winner.revenue)})."
    )


def _build_best_financial_health(
    snapshots: list[CompanySnapshot],
) -> str:
    winner = _best_financial_health(snapshots)

    if winner is None:
        return "Insufficient financial health data across the universe."

    return (
        f"Strongest financial health: {winner.company} "
        f"(Altman Z {_format_ratio(winner.altman_z)}, "
        f"Piotroski F {winner.piotroski_f if winner.piotroski_f is not None else 'N/A'}, "
        f"classification {winner.risk_classification or 'N/A'})."
    )


def _build_highest_risk(
    snapshots: list[CompanySnapshot],
) -> str:
    riskiest = _highest_risk(snapshots)

    if riskiest is None:
        return "No risk data available."

    top_risks = riskiest.identified_risks[:3]
    risk_names = (
        ", ".join(item["risk"] for item in top_risks)
        if top_risks
        else "N/A"
    )

    return (
        f"Highest risk profile: {riskiest.company} "
        f"(classification {riskiest.risk_classification or 'N/A'}, "
        f"Altman Z {_format_ratio(riskiest.altman_z)}, "
        f"rule recommendation {riskiest.rule_recommendation or 'N/A'}).\n"
        f"Top identified SEC risks: {risk_names}."
    )


def _build_risk_comparison(
    snapshots: list[CompanySnapshot],
) -> str:
    blocks = []

    for row in snapshots:
        lines = [
            f"{row.company}:",
            f"  Risk classification: {row.risk_classification or 'N/A'}",
            f"  Altman Z: {_format_ratio(row.altman_z)}",
            f"  Piotroski F: {row.piotroski_f if row.piotroski_f is not None else 'N/A'}",
        ]

        if row.identified_risks:
            lines.append("  Top SEC risks:")
            for item in row.identified_risks[:3]:
                lines.append(
                    f"    - {item['risk']} ({item['severity']}): "
                    f"{item['summary'][:120]}..."
                )
        else:
            lines.append("  Top SEC risks: None identified")

        blocks.append("\n".join(lines))

    return "\n\n".join(blocks)


def _build_final_recommendations(
    snapshots: list[CompanySnapshot],
) -> str:
    lines = []

    for row in snapshots:
        aligned = (
            row.rule_recommendation == row.ml_recommendation
            and row.rule_recommendation in {"BUY", "HOLD", "AVOID"}
        )

        if aligned:
            stance = (
                f"Aligned BUY/HOLD/AVOID signal: {row.rule_recommendation}"
            )
        elif row.ml_recommendation == "UNAVAILABLE":
            stance = (
                f"Rule-based only: {row.rule_recommendation or 'N/A'}"
            )
        else:
            stance = (
                f"Rule {row.rule_recommendation or 'N/A'} vs "
                f"ML {row.ml_recommendation or 'N/A'} — review divergence"
            )

        lines.append(
            f"{row.company} (rank #{row.rank}): {stance}. "
            f"ML confidence: {row.ml_confidence or 'N/A'}."
        )

    return "\n".join(lines)


def generate_committee_report(
    snapshots: list[CompanySnapshot],
) -> str:
    ranked = rank_companies(snapshots)
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")

    sections = [
        (
            "INVESTMENT COMMITTEE REPORT",
            f"Generated: {generated}\n"
            f"Universe: {len(ranked)} companies",
        ),
        ("A. EXECUTIVE SUMMARY", _build_executive_summary(ranked)),
        ("B. COMPANY RANKING", _build_company_ranking(ranked)),
        (
            "C. FINANCIAL COMPARISON TABLE",
            _build_financial_table(ranked),
        ),
        ("D. BEST GROWTH", _build_best_growth(ranked)),
        (
            "E. BEST FINANCIAL HEALTH",
            _build_best_financial_health(ranked),
        ),
        ("F. HIGHEST RISK", _build_highest_risk(ranked)),
        ("G. RISK COMPARISON", _build_risk_comparison(ranked)),
        (
            "H. FINAL RECOMMENDATIONS",
            _build_final_recommendations(ranked),
        ),
    ]

    blocks = []
    for title, body in sections:
        separator = "=" * len(title)
        blocks.append(f"{title}\n{separator}\n\n{body}")

    return "\n\n".join(blocks) + "\n"


def save_report(
    report_text: str,
    report_path: str = REPORT_PATH,
) -> str:
    os.makedirs(
        os.path.dirname(report_path),
        exist_ok=True,
    )

    with open(report_path, "w", encoding="utf-8") as report_file:
        report_file.write(report_text)

    return report_path


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "\nUsage:\n"
            "python compare_report.py Apple Microsoft Nvidia Tesla Amazon\n"
        )
        sys.exit(1)

    companies = sys.argv[1:]
    snapshots = []

    print(
        f"\nBuilding investment committee report for "
        f"{len(companies)} companies...\n"
    )

    for company_name in companies:
        print(f"Analyzing {company_name}...")
        snapshots.append(
            collect_company_snapshot(company_name)
        )

    report_text = generate_committee_report(snapshots)
    report_path = save_report(report_text)

    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()
