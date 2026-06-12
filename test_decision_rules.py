from nodes.decision_rules import (
    generate_recommendation,
    generate_confidence
)

print(
    generate_recommendation(
        8.57,
        7
    )
)

print(
    generate_confidence(
        8.57,
        7
    )
)