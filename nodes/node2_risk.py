
from state import FinancialData
from state import (
    AgentState,
    RiskMetrics
)


def calculate_working_capital(
    financials: FinancialData
) -> float:

    current = financials.current_year

    return (
        current.current_assets
        - current.current_liabilities
    )


def calculate_altman_z_score(
    financials: FinancialData,
    market_value_equity: float
) -> dict:

    current = financials.current_year

    working_capital = (
        current.current_assets
        - current.current_liabilities
    )

    a = (
        working_capital
        / current.total_assets
    )

    b = (
        current.retained_earnings
        / current.total_assets
    )

    c = (
        current.ebit
        / current.total_assets
    )

    d = (
        market_value_equity
        / current.total_liabilities
    )

    e = (
        current.revenue
        / current.total_assets
    )

    z_score = (
        1.2 * a
        + 1.4 * b
        + 3.3 * c
        + 0.6 * d
        + 1.0 * e
    )

    return {
        "working_capital_ratio": a,
        "retained_earnings_ratio": b,
        "ebit_ratio": c,
        "market_value_ratio": d,
        "asset_turnover_ratio": e,
        "altman_z_score": z_score,
    }


def classify_altman_score(
    z_score: float
) -> str:

    if z_score > 3:
        return "Safe Zone"

    if z_score > 1.8:
        return "Grey Zone"

    return "Distress Zone"


def calculate_piotroski_f_score(
    financials: FinancialData
):

    current = financials.current_year
    previous = financials.previous_year

    score = 0

    if (
        current.net_income is not None
        and current.net_income > 0
    ):
        score += 1

    if (
        current.operating_cash_flow is not None
        and current.operating_cash_flow > 0
    ):
        score += 1

    if (
        current.net_income is not None
        and current.total_assets is not None
        and previous.net_income is not None
        and previous.total_assets is not None
    ):

        current_roa = (
            current.net_income /
            current.total_assets
        )

        previous_roa = (
            previous.net_income /
            previous.total_assets
        )

        if current_roa > previous_roa:
            score += 1

    if (
        current.operating_cash_flow is not None
        and current.net_income is not None
        and current.operating_cash_flow >
        current.net_income
    ):
        score += 1

    if (
        current.long_term_debt is not None
        and previous.long_term_debt is not None
        and current.long_term_debt <
        previous.long_term_debt
    ):
        score += 1

    if (
        current.current_assets is not None
        and current.current_liabilities is not None
        and previous.current_assets is not None
        and previous.current_liabilities is not None
    ):

        current_ratio = (
            current.current_assets /
            current.current_liabilities
        )

        previous_ratio = (
            previous.current_assets /
            previous.current_liabilities
        )

        if current_ratio > previous_ratio:
            score += 1

    if (
        current.shares_outstanding is not None
        and previous.shares_outstanding is not None
        and current.shares_outstanding <=
        previous.shares_outstanding
    ):
        score += 1

    if (
        current.gross_profit is not None
        and previous.gross_profit is not None
        and current.revenue is not None
        and previous.revenue is not None
        and current.revenue != 0
        and previous.revenue != 0
    ):

        current_margin = (
            current.gross_profit /
            current.revenue
        )

        previous_margin = (
            previous.gross_profit /
            previous.revenue
        )

        if current_margin > previous_margin:
            score += 1

    if (
        current.revenue is not None
        and previous.revenue is not None
        and current.total_assets is not None
        and previous.total_assets is not None
        and current.total_assets != 0
        and previous.total_assets != 0
    ):

        current_turnover = (
            current.revenue /
            current.total_assets
        )

        previous_turnover = (
            previous.revenue /
            previous.total_assets
        )

        if current_turnover > previous_turnover:
            score += 1

    return score

def classify_piotroski_score(
    score: int
):

    if score >= 7:
        return "Strong"

    if score >= 4:
        return "Average"

    return "Weak"

def run_risk_analysis(
    state: AgentState
) -> AgentState:

    financials = state.financial_data

    altman_results = (
        calculate_altman_z_score(
            financials,
            3000000
        )
    )

    piotroski_score = (
        calculate_piotroski_f_score(
            financials
        )
    )

    state.risk_metrics = RiskMetrics(
        altman_z_score=
            altman_results[
                "altman_z_score"
            ],

        piotroski_f_score=
            piotroski_score,

        risk_classification=
            classify_altman_score(
                altman_results[
                    "altman_z_score"
                ]
            )
    )

    return state


if __name__ == "__main__":

    from nodes.node0_sec import (
        run_sec_raw_ingestion
    )

    from utils.xbrl_parser import (
        extract_financial_data_xbrl
    )

    filing_text = run_sec_raw_ingestion(
        "Apple"
    )

    financials = (
        extract_financial_data_xbrl(
            filing_text
        )
    )

    results = calculate_altman_z_score(
        financials,
        3000000
    )

    print("\n===== ALTMAN Z SCORE =====\n")

    for key, value in results.items():
        print(f"{key}: {value}")

    print(
        "\nClassification:",
        classify_altman_score(
            results["altman_z_score"]
        )
    )

    piotroski_score = (
        calculate_piotroski_f_score(
            financials
        )
    )

    print(
        "\n===== PIOTROSKI F SCORE =====\n"
    )

    print(
        "Piotroski F Score:",
        piotroski_score
    )

    print(
        "Financial Strength:",
        classify_piotroski_score(
            piotroski_score
        )
    )

    state = AgentState(
        company_name="Apple",
        financial_data=financials
    )

    state = run_risk_analysis(
        state
    )

    print("\nSTATE OUTPUT\n")

    print(
        state.risk_metrics
    )