from utils.sec_parser import (
    extract_main_10k
)

text = extract_main_10k(
    "data/sec_filings/sec-edgar-filings/AAPL/10-K/0000320193-25-000079/full-submission.txt"
)

print("Characters:", len(text))

print("\n\n")

print(
    text[100000:105000]
)