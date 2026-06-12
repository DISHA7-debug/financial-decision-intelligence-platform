def generate_recommendation(
    altman_score: float,
    piotroski_score: int
):

    if (
        altman_score >= 5
        and piotroski_score >= 7
    ):
        return "BUY"

    if (
        altman_score >= 3
        and piotroski_score >= 5
    ):
        return "HOLD"

    return "AVOID"


def generate_confidence(
    altman_score: float,
    piotroski_score: int
):

    if (
        altman_score >= 5
        and piotroski_score >= 7
    ):
        return "HIGH"

    if (
        altman_score >= 3
        and piotroski_score >= 5
    ):
        return "MEDIUM"

    return "LOW"