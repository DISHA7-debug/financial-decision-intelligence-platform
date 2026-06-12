from nodes.node0_sec import run_sec_ingestion
from nodes.node1_ingest import run_ingestion_from_text

text = run_sec_ingestion("Apple")

financials = run_ingestion_from_text(
    text=text,
    cache_key="apple_sec"
)

print(financials)