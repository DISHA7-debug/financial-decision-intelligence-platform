from state import (
    AgentState,
    DecisionOutput
)


def generate_recommendation(
    altman_score: float | None,
    piotroski_score: int | None,
) -> str:
    if (
        altman_score is not None
        and piotroski_score is not None
        and altman_score > 3
        and piotroski_score >= 7
    ):
        return "BUY"

    if (
        altman_score is not None
        and piotroski_score is not None
        and altman_score > 3
        and piotroski_score >= 4
    ):
        return "HOLD"

    return "AVOID"


def generate_confidence(
    altman_score: float | None,
    piotroski_score: int | None,
) -> str:
    recommendation = generate_recommendation(
        altman_score,
        piotroski_score,
    )

    if recommendation == "BUY":
        return "HIGH"

    if recommendation == "HOLD":
        return "MEDIUM"

    return "HIGH"


def generate_rule_memo(
    altman_score: float | None,
    piotroski_score: int | None,
    recommendation: str,
    confidence: str,
) -> str:
    altman_text = (
        f"{altman_score:.2f}"
        if altman_score is not None
        else "N/A"
    )
    piotroski_text = (
        str(piotroski_score)
        if piotroski_score is not None
        else "N/A"
    )

    return (
        f"Rule-based decision: {recommendation} "
        f"({confidence} confidence). "
        f"Altman Z-Score={altman_text}, "
        f"Piotroski F-Score={piotroski_text}."
    )


def run_rule_decision(
    state: AgentState
) -> AgentState:
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

    recommendation = generate_recommendation(
        altman_score,
        piotroski_score,
    )
    confidence = generate_confidence(
        altman_score,
        piotroski_score,
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
