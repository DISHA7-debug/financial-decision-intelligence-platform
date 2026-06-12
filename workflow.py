import sys

from state import (
    AgentState,
)

from nodes.node0_sec import (
    run_sec_raw_ingestion
)

from nodes.node1_ingest import (
    run_ingestion_from_text
)

from nodes.node2_risk import (
    run_risk_analysis
)

from nodes.node3_rag import (
    run_retrieval
)

from nodes.node4_rules import (
    run_rule_decision
)

from nodes.node4_decision import (
    run_decision
)


def run_workflow(
    company_name: str
) -> AgentState:

    filing_text = run_sec_raw_ingestion(
    company_name
    )

    financial_data = (
        run_ingestion_from_text(
            text=filing_text,
            cache_key=f"{company_name.lower()}_sec"
        )
    )

    state = AgentState(
        company_name=company_name,
        financial_data=financial_data
    )

    state = run_risk_analysis(
        state
    )

    state = run_retrieval(
        state,
        "major business risks",
        
    )

    state = run_rule_decision(
        state
    )

    state = run_decision(
        state
    )

    return state


if __name__ == "__main__":

    if len(sys.argv) < 2:

        print(
            "\nUsage:\n"
            "python workflow.py Apple\n"
        )

        sys.exit()

    company_name = sys.argv[1]

    state = run_workflow(
        company_name
    )

    print(
        "\n===== FINAL STATE =====\n"
    )

    print(state)
