import json
import os

from google import genai
from dotenv import load_dotenv

from state import (
    AgentState,
    DecisionOutput
)

from prompts.decision_json_prompt import (
    DECISION_JSON_PROMPT
)

from nodes.node4_rules import (
    generate_rule_memo,
    run_rule_decision,
)

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def _generate_llm_memo(
    state: AgentState,
    recommendation: str,
    confidence: str,
) -> str:
    prompt = DECISION_JSON_PROMPT.format(
        recommendation=recommendation,
        confidence=confidence,
        altman_score=state.risk_metrics.altman_z_score,
        piotroski_score=state.risk_metrics.piotroski_f_score,
        evidence=state.retrieved_context,
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    raw = response.text.strip()
    raw = raw.replace("```json", "")
    raw = raw.replace("```", "")
    raw = raw.strip()

    data = json.loads(raw)

    return data["memo"]


def run_decision(
    state: AgentState
) -> AgentState:
    if state.decision_output is None:
        state = run_rule_decision(state)

    recommendation = (
        state.decision_output.recommendation
    )
    confidence = (
        state.decision_output.confidence
    )
    altman_score = (
        state.risk_metrics.altman_z_score
        if state.risk_metrics
        else None
    )
    piotroski_score = (
        state.risk_metrics.piotroski_f_score
        if state.risk_metrics
        else None
    )

    try:
        memo = _generate_llm_memo(
            state,
            recommendation,
            confidence,
        )
    except Exception as error:
        print(
            "\nLLM memo generation failed, "
            "using rule-based memo:\n",
            error,
        )
        memo = generate_rule_memo(
            altman_score,
            piotroski_score,
            recommendation,
            confidence,
        )

    state.decision_output = DecisionOutput(
        recommendation=recommendation,
        confidence=confidence,
        memo=memo,
    )

    return state
