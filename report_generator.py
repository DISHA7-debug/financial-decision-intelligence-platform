import os
import sys

# macOS Apple Silicon: PyTorch (RAG) and XGBoost both link libomp.
# These must be set before either library is imported/loaded.
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")

from datetime import datetime
from typing import TYPE_CHECKING

from risk_intelligence import (
    extract_identified_risks,
    format_identified_risks,
)
from state import AgentState

if TYPE_CHECKING:
    from ml.predict_xgboost import MLPrediction
from workflow import run_workflow

REPORTS_DIR = "reports"


def _format_millions(value: float | None) -> str:
    if value is None:
        return "N/A"

    return f"${value:,.0f}M"


def _format_ratio(value: float | None) -> str:
    if value is None:
        return "N/A"

    return f"{value:.2f}"


def _format_percent(value: float | None) -> str:
    if value is None:
        return "N/A"

    return f"{value * 100:.1f}%"


def _build_top_identified_risks(state: AgentState) -> str:
    identified_risks = extract_identified_risks(
        state.retrieved_context
    )
    return format_identified_risks(identified_risks)


def _final_investment_view(
    rule_recommendation: str | None,
    ml_recommendation: str,
) -> str:
    rule = rule_recommendation or "UNAVAILABLE"
    ml = ml_recommendation

    if rule == ml and rule in {"BUY", "HOLD", "AVOID"}:
        return (
            f"Aligned view: both the rule engine and ML model "
            f"recommend {rule}. This consistency supports a "
            f"{rule} stance pending qualitative review."
        )

    if ml == "UNAVAILABLE":
        return (
            f"Rule-based recommendation is {rule}. ML model output "
            f"is unavailable; rely on fundamentals and SEC context."
        )

    if rule in {"BUY", "HOLD", "AVOID"} and ml in {
        "BUY",
        "HOLD",
        "AVOID",
    }:
        return (
            f"Divergent signals: rules suggest {rule} while ML "
            f"suggests {ml}. Treat this as a HOLD pending deeper "
            f"review of financial trends and disclosed risks."
        )

    return (
        "Insufficient structured signals for a definitive view. "
        "Further diligence is required."
    )


def _build_executive_summary(
    state: AgentState,
    ml_prediction: "MLPrediction",
) -> str:
    company = state.company_name
    financials = state.financial_data
    risk = state.risk_metrics
    decision = state.decision_output

    revenue = None
    net_income = None
    if financials:
        revenue = financials.current_year.revenue
        net_income = financials.current_year.net_income

    rule_rec = (
        decision.recommendation
        if decision and decision.recommendation
        else "N/A"
    )
    risk_class = (
        risk.risk_classification
        if risk and risk.risk_classification
        else "N/A"
    )

    return (
        f"{company} due diligence review synthesizes XBRL financials, "
        f"quantitative risk scores, SEC risk-factor retrieval, rule-based "
        f"scoring, and an XGBoost recommendation model.\n\n"
        f"Latest revenue: {_format_millions(revenue)} | "
        f"Net income: {_format_millions(net_income)} | "
        f"Risk classification: {risk_class} | "
        f"Rule recommendation: {rule_rec} | "
        f"ML recommendation: {ml_prediction.recommendation} "
        f"({ml_prediction.confidence} confidence)."
    )


def _build_financial_health(state: AgentState) -> str:
    if state.financial_data is None:
        return "Financial data unavailable."

    current = state.financial_data.current_year
    previous = state.financial_data.previous_year

    revenue_growth = None
    if (
        current.revenue is not None
        and previous.revenue is not None
        and previous.revenue != 0
    ):
        revenue_growth = (
            (current.revenue - previous.revenue)
            / previous.revenue
        )

    current_ratio = None
    if (
        current.current_assets is not None
        and current.current_liabilities is not None
        and current.current_liabilities != 0
    ):
        current_ratio = (
            current.current_assets
            / current.current_liabilities
        )

    debt_ratio = None
    if (
        current.total_liabilities is not None
        and current.total_assets is not None
        and current.total_assets != 0
    ):
        debt_ratio = (
            current.total_liabilities
            / current.total_assets
        )

    gross_margin = None
    if (
        current.gross_profit is not None
        and current.revenue is not None
        and current.revenue != 0
    ):
        gross_margin = current.gross_profit / current.revenue

    lines = [
        "Income Statement (current FY, USD millions):",
        f"  Revenue:          {_format_millions(current.revenue)}",
        f"  Previous revenue: {_format_millions(previous.revenue)}",
        f"  Revenue growth:   {_format_percent(revenue_growth)}",
        f"  Net income:       {_format_millions(current.net_income)}",
        f"  Gross profit:     {_format_millions(current.gross_profit)}",
        f"  Gross margin:     {_format_percent(gross_margin)}",
        f"  EBIT:             {_format_millions(current.ebit)}",
        "",
        "Balance Sheet & Cash Flow:",
        f"  Total assets:        {_format_millions(current.total_assets)}",
        f"  Total liabilities:   {_format_millions(current.total_liabilities)}",
        f"  Current ratio:       {_format_ratio(current_ratio)}",
        f"  Debt ratio:          {_format_ratio(debt_ratio)}",
        f"  Operating cash flow: {_format_millions(current.operating_cash_flow)}",
        f"  Long-term debt:      {_format_millions(current.long_term_debt)}",
    ]

    return "\n".join(lines)


def _build_risk_analysis(state: AgentState) -> str:
    risk = state.risk_metrics
    if risk is None:
        return "Risk metrics unavailable."

    return (
        f"Altman Z-Score:      {_format_ratio(risk.altman_z_score)}\n"
        f"Piotroski F-Score:   {risk.piotroski_f_score if risk.piotroski_f_score is not None else 'N/A'}\n"
        f"Risk classification: {risk.risk_classification or 'N/A'}\n\n"
        "Interpretation:\n"
        "  Altman Z > 3.0 indicates low bankruptcy risk.\n"
        "  Piotroski F-Score ranges from 0-9; higher scores reflect stronger fundamentals."
    )


def _build_rule_recommendation(state: AgentState) -> str:
    decision = state.decision_output
    if decision is None:
        return "Rule-based recommendation unavailable."

    lines = [
        f"Recommendation: {decision.recommendation or 'N/A'}",
        f"Confidence:     {decision.confidence or 'N/A'}",
    ]

    if decision.memo:
        lines.extend(["", "Memo:", decision.memo.strip()])

    return "\n".join(lines)


def _build_ml_recommendation(
    ml_prediction: "MLPrediction",
) -> str:
    lines = [
        f"Recommendation: {ml_prediction.recommendation}",
        f"Confidence:     {ml_prediction.confidence}",
        "",
        "Model features (input vector):",
    ]

    for feature, value in ml_prediction.features.items():
        if value is None:
            formatted = "N/A"
        elif feature == "revenue_growth":
            formatted = _format_percent(value)
        elif feature == "net_income":
            formatted = _format_millions(value)
        elif feature in {"gross_margin", "debt_ratio"}:
            formatted = _format_percent(value)
        elif feature == "piotroski_f":
            formatted = f"{int(value)}"
        else:
            formatted = _format_ratio(value)

        lines.append(f"  {feature}: {formatted}")

    if ml_prediction.probabilities:
        lines.extend(["", "Class probabilities:"])
        for label, probability in sorted(
            ml_prediction.probabilities.items(),
            key=lambda item: item[1],
            reverse=True,
        ):
            lines.append(
                f"  {label}: {probability * 100:.1f}%"
            )

    return "\n".join(lines)


def generate_report(
    state: AgentState,
    ml_prediction=None,
) -> str:
    from ml.predict_xgboost import predict_recommendation

    if ml_prediction is None:
        ml_prediction = predict_recommendation(state)

    decision = state.decision_output
    rule_rec = (
        decision.recommendation if decision else None
    )

    sections = [
        (
            "DUE DILIGENCE REPORT",
            (
                f"Company: {state.company_name}\n"
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            ),
        ),
        ("EXECUTIVE SUMMARY", _build_executive_summary(state, ml_prediction)),
        ("FINANCIAL HEALTH", _build_financial_health(state)),
        ("RISK ANALYSIS", _build_risk_analysis(state)),
        (
            "TOP IDENTIFIED RISKS",
            _build_top_identified_risks(state),
        ),
        (
            "RULE-BASED RECOMMENDATION",
            _build_rule_recommendation(state),
        ),
        (
            "ML RECOMMENDATION",
            _build_ml_recommendation(ml_prediction),
        ),
        (
            "FINAL INVESTMENT VIEW",
            _final_investment_view(
                rule_rec,
                ml_prediction.recommendation,
            ),
        ),
    ]

    blocks = []
    for title, body in sections:
        separator = "=" * len(title)
        blocks.append(f"{title}\n{separator}\n\n{body}")

    return "\n\n".join(blocks) + "\n"


def save_report(
    company_name: str,
    report_text: str,
    reports_dir: str = REPORTS_DIR,
) -> str:
    os.makedirs(reports_dir, exist_ok=True)

    filename = f"{company_name.lower()}_report.txt"
    report_path = os.path.join(reports_dir, filename)

    with open(report_path, "w", encoding="utf-8") as report_file:
        report_file.write(report_text)

    return report_path


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "\nUsage:\n"
            "python report_generator.py Apple\n"
        )
        sys.exit(1)

    company_name = sys.argv[1]

    print(f"\nRunning due diligence workflow for {company_name}...")
    state = run_workflow(company_name)

    from ml.predict_xgboost import predict_recommendation

    print("Generating ML prediction...")
    ml_prediction = predict_recommendation(state)

    print("Writing report...")
    report_text = generate_report(state, ml_prediction)
    report_path = save_report(company_name, report_text)

    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()
