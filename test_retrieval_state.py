from state import (
    AgentState,
    FinancialData,
    FinancialYear
)

from nodes.node3_rag import (
    run_retrieval
)

state = AgentState(
    company_name="Apple",
    financial_data=FinancialData(
        current_year=FinancialYear(),
        previous_year=FinancialYear()
    )
)

state = run_retrieval(
    state,
    "major business risks"
)

print(
    state.retrieved_context[:1000]
)