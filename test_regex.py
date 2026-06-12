import re

from nodes.node0_sec import (
    run_sec_raw_ingestion
)

text = run_sec_raw_ingestion(
    "Apple"
)

pattern = (
    r"<us-gaap:Assets[^>]*>"
    r"(-?\d+)"
    r"</us-gaap:Assets>"
)

matches = re.findall(
    pattern,
    text,
    re.IGNORECASE
)

print("COUNT:", len(matches))
print(matches[:10])