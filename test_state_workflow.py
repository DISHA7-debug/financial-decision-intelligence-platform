from state import (
    FinancialYear,
    FinancialData,
    AgentState
)

from nodes.node2_risk import (
    run_risk_analysis
)

current_year = FinancialYear(
    revenue=416161.0,
    net_income=112010.0,
    total_assets=359241.0,
    total_liabilities=285508.0,
    current_assets=147957.0,
    current_liabilities=165631.0,
    retained_earnings=-14264.0,
    ebit=133050.0,
    long_term_debt=78328.0,
    gross_profit=195201.0,
    shares_outstanding=14948500.0
)

previous_year = FinancialYear(
    revenue=391035.0,
    net_income=93736.0,
    total_assets=364980.0,
    total_liabilities=308030.0,
    current_assets=152987.0,
    current_liabilities=176392.0,
    retained_earnings=-19154.0,
    ebit=123216.0,
    long_term_debt=85750.0,
    gross_profit=180683.0,
    shares_outstanding=15343783.0
)

financial_data = FinancialData(
    current_year=current_year,
    previous_year=previous_year
)

state = AgentState(
    company_name="Apple",
    financial_data=financial_data
)

state = run_risk_analysis(
    state
)

print("\nSTATE\n")
print(state)