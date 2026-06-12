from state import AgentState

from nodes.node0_sec import (
    run_sec_ingestion
)

from nodes.node1_ingest import (
    run_ingestion_from_text
)

from nodes.node3_rag import (
    run_retrieval
)

text = run_sec_ingestion(
    "Apple"
)

financial_data = run_ingestion_from_text(
    text=text,
    cache_key="apple_sec"
)

state = AgentState(
    company_name="Apple",
    financial_data=financial_data
)

state = run_retrieval(
    state,
    "major business risks"
)

print(
    state.retrieved_context[:3000]
)
