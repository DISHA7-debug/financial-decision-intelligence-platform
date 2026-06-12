DECISION_JSON_PROMPT = """
You are a senior financial analyst.

A recommendation and confidence level have already been determined.

Recommendation:
{recommendation}

Confidence:
{confidence}

Altman Z Score:
{altman_score}

Piotroski F Score:
{piotroski_score}

Evidence:
{evidence}

Return ONLY valid JSON.

Example:

{{
    "memo": "Detailed investment explanation here"
}}
"""