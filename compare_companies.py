from dataclasses import dataclass

from workflow import run_workflow

COMPANIES = [
    "Apple",
    "Microsoft",
    "Nvidia",
]

RECOMMENDATION_RANK = {
    "BUY": 3,
    "HOLD": 2,
    "AVOID": 1,
    "ERROR": 0,
}


@dataclass
class CompanyComparison:
    company: str
    revenue: float | None
    net_income: float | None
    altman_z: float | None
    piotroski_f: int | None
    risk_classification: str | None
    recommendation: str | None
    rank: int | None = None


def _format_millions(
    value: float | None
) -> str:
    if value is None:
        return "N/A"

    return f"{value:,.0f}"


def _format_altman(
    value: float | None
) -> str:
    if value is None:
        return "N/A"

    return f"{value:.2f}"


def collect_company_metrics(
    company_name: str
) -> CompanyComparison:
    try:
        state = run_workflow(company_name)
    except Exception as error:
        print(
            f"Failed to analyze {company_name}: {error}\n"
        )
        return CompanyComparison(
            company=company_name,
            revenue=None,
            net_income=None,
            altman_z=None,
            piotroski_f=None,
            risk_classification=None,
            recommendation="ERROR",
        )

    financials = state.financial_data
    risk = state.risk_metrics
    decision = state.decision_output

    return CompanyComparison(
        company=company_name,
        revenue=(
            financials.current_year.revenue
            if financials else None
        ),
        net_income=(
            financials.current_year.net_income
            if financials else None
        ),
        altman_z=(
            risk.altman_z_score
            if risk else None
        ),
        piotroski_f=(
            risk.piotroski_f_score
            if risk else None
        ),
        risk_classification=(
            risk.risk_classification
            if risk else None
        ),
        recommendation=(
            decision.recommendation
            if decision else None
        ),
    )


def rank_companies(
    results: list[CompanyComparison]
) -> list[CompanyComparison]:
    ranked = sorted(
        results,
        key=lambda row: (
            RECOMMENDATION_RANK.get(
                row.recommendation or "",
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


def print_comparison_table(
    results: list[CompanyComparison]
) -> None:
    headers = (
        "Rank",
        "Company",
        "Revenue (M)",
        "Net Income (M)",
        "Altman Z",
        "Piotroski F",
        "Risk Classification",
        "Recommendation",
    )

    rows = [
        (
            str(row.rank or ""),
            row.company,
            _format_millions(row.revenue),
            _format_millions(row.net_income),
            _format_altman(row.altman_z),
            str(row.piotroski_f if row.piotroski_f is not None else "N/A"),
            row.risk_classification or "N/A",
            row.recommendation or "N/A",
        )
        for row in results
    ]

    widths = [
        max(len(headers[i]), *(len(row[i]) for row in rows))
        for i in range(len(headers))
    ]

    header_line = " | ".join(
        headers[i].ljust(widths[i])
        for i in range(len(headers))
    )
    separator = "-+-".join(
        "-" * widths[i]
        for i in range(len(headers))
    )

    print("\n===== COMPANY COMPARISON =====\n")
    print(header_line)
    print(separator)

    for row in rows:
        print(
            " | ".join(
                row[i].ljust(widths[i])
                for i in range(len(headers))
            )
        )

    print()


def compare_companies(
    companies: list[str]
) -> list[CompanyComparison]:
    results = []

    for company_name in companies:
        print(f"\nAnalyzing {company_name}...\n")
        results.append(
            collect_company_metrics(company_name)
        )

    ranked = rank_companies(results)
    print_comparison_table(ranked)

    return ranked


if __name__ == "__main__":
    compare_companies(COMPANIES)
