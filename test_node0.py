from nodes.node0_sec import (
    run_sec_ingestion
)

text = run_sec_ingestion(
    "Apple"
)

print(
    len(text)
)

print(
    text[:1000]
)