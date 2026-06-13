import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")

from compare_report import (  # noqa: E402
    REPORT_PATH,
    collect_company_snapshot,
    generate_committee_report,
    rank_companies,
    save_report as save_committee_report,
)
from ml.predict_xgboost import predict_recommendation  # noqa: E402
from nodes.node0_sec import resolve_ticker  # noqa: E402
from report_generator import (  # noqa: E402
    REPORTS_DIR,
    generate_report,
    save_report,
)
from risk_intelligence import extract_identified_risks  # noqa: E402
from workflow import run_workflow  # noqa: E402

from backend.schemas import (  # noqa: E402
    AnalyzeResponse,
    CommitteeReportResponse,
    ComparisonItem,
    CompareResponse,
    RankingItem,
    ReportResponse,
    RiskItem,
)


class CompanyNotFoundError(Exception):
    pass


class WorkflowError(Exception):
    pass


class ReportNotFoundError(Exception):
    pass


class ModelLoadError(Exception):
    pass


def validate_company(company: str) -> str:
    try:
        resolve_ticker(company)
    except KeyError as error:
        raise CompanyNotFoundError(
            f"Unknown company or ticker: {company}"
        ) from error

    return company.strip()


def _safe_ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None:
        return None
    if denominator == 0:
        return None
    return numerator / denominator


def analyze_company(company: str) -> AnalyzeResponse:
    validate_company(company)

    try:
        state = run_workflow(company)
    except Exception as error:
        raise WorkflowError(
            f"Workflow failed for {company}: {error}"
        ) from error

    try:
        ml_prediction = predict_recommendation(state)
    except Exception as error:
        raise ModelLoadError(
            f"ML prediction failed for {company}: {error}"
        ) from error

    if ml_prediction.recommendation == "UNAVAILABLE":
        raise ModelLoadError(
            "XGBoost model artifacts are missing or could not be loaded"
        )

    decision = state.decision_output
    risk = state.risk_metrics
    identified = extract_identified_risks(
        state.retrieved_context
    )
    financials = state.financial_data
    current = financials.current_year if financials else None

    revenue = current.revenue if current else None
    net_income = current.net_income if current else None
    gross_margin = _safe_ratio(
        current.gross_profit if current else None,
        revenue,
    )
    current_ratio = _safe_ratio(
        current.current_assets if current else None,
        current.current_liabilities if current else None,
    )

    return AnalyzeResponse(
        company=company,
        recommendation=(
            decision.recommendation if decision else "N/A"
        ),
        confidence=(
            decision.confidence if decision else "N/A"
        ),
        altman_z=(
            risk.altman_z_score if risk else None
        ),
        piotroski_f=(
            risk.piotroski_f_score if risk else None
        ),
        revenue=revenue,
        net_income=net_income,
        gross_margin=gross_margin,
        current_ratio=current_ratio,
        risk_classification=(
            risk.risk_classification if risk else None
        ),
        identified_risks=[
            RiskItem(**item) for item in identified
        ],
        ml_recommendation=ml_prediction.recommendation,
        ml_confidence=ml_prediction.confidence,
    )


def compare_companies_api(
    companies: list[str],
) -> CompareResponse:
    for company in companies:
        validate_company(company)

    snapshots = [
        collect_company_snapshot(company)
        for company in companies
    ]
    ranked = rank_companies(snapshots)

    ranking = [
        RankingItem(
            rank=row.rank or 0,
            company=row.company,
            revenue=row.revenue,
            growth=row.revenue_growth,
            recommendation=row.rule_recommendation,
            ml_recommendation=row.ml_recommendation,
            altman_z=row.altman_z,
            piotroski_f=row.piotroski_f,
            risk_classification=row.risk_classification,
        )
        for row in ranked
    ]

    comparison = [
        ComparisonItem(
            company=row.company,
            revenue=row.revenue,
            revenue_growth=row.revenue_growth,
            net_income=row.net_income,
            current_ratio=row.current_ratio,
            debt_ratio=row.debt_ratio,
            altman_z=row.altman_z,
            piotroski_f=row.piotroski_f,
            risk_classification=row.risk_classification,
            rule_recommendation=row.rule_recommendation,
            ml_recommendation=row.ml_recommendation,
            rank=row.rank,
        )
        for row in ranked
    ]

    report_text = generate_committee_report(snapshots)
    save_committee_report(report_text)

    return CompareResponse(
        ranking=ranking,
        comparison=comparison,
    )


def get_company_report(
    company: str,
    generate_if_missing: bool = True,
) -> ReportResponse:
    validate_company(company)

    report_path = os.path.join(
        REPORTS_DIR,
        f"{company.lower()}_report.txt",
    )

    if os.path.exists(report_path):
        with open(report_path, encoding="utf-8") as report_file:
            content = report_file.read()

        return ReportResponse(
            company=company,
            report_path=report_path,
            content=content,
        )

    if not generate_if_missing:
        raise ReportNotFoundError(
            f"No report found for {company}"
        )

    try:
        state = run_workflow(company)
        ml_prediction = predict_recommendation(state)
    except Exception as error:
        raise WorkflowError(
            f"Failed to generate report for {company}: {error}"
        ) from error

    if ml_prediction.recommendation == "UNAVAILABLE":
        raise ModelLoadError(
            "XGBoost model artifacts are missing or could not be loaded"
        )

    report_text = generate_report(state, ml_prediction)
    saved_path = save_report(company, report_text)

    return ReportResponse(
        company=company,
        report_path=saved_path,
        content=report_text,
    )


def get_committee_report() -> CommitteeReportResponse:
    if not os.path.exists(REPORT_PATH):
        raise ReportNotFoundError(
            "Investment committee report has not been generated yet. "
            "Run POST /compare first."
        )

    with open(REPORT_PATH, encoding="utf-8") as report_file:
        content = report_file.read()

    return CommitteeReportResponse(
        report_path=REPORT_PATH,
        content=content,
    )
