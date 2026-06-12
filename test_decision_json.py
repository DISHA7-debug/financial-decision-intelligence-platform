from state import (
    FinancialYear,
    FinancialData,
    AgentState,
    RiskMetrics
)

from nodes.node4_decision import (
    run_decision
)

state = AgentState(
    company_name="Apple",
    financial_data=FinancialData(
        current_year=FinancialYear(),
        previous_year=FinancialYear()
    ),

    risk_metrics=RiskMetrics(
        altman_z_score=8.57,
        piotroski_f_score=7,
        risk_classification="Safe Zone"
    ),

    retrieved_context="""
Apple faces risks from competition,
supply chain disruptions,
regulatory scrutiny,
and macroeconomic conditions.
"""
)

state = run_decision(
    state
)

print("\n===== DECISION OUTPUT =====\n")

print(
    state.decision_output
)