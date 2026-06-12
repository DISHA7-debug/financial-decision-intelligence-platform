from indexing.retriever import retrieve

from state import AgentState


def run_retrieval(
    state: AgentState,
    query: str
) -> AgentState:

    retrieved_docs = retrieve(
        query=query,
        company=state.company_name,
        top_k=5
    )

    context = ""

    for doc in retrieved_docs:

        context += f"""
Company: {doc['company']}
Source: {doc['source']}

{doc['text']}

====================
"""

    state.retrieved_context = context

    return state