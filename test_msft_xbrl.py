from nodes.node0_sec import (
    run_sec_raw_ingestion
)

from utils.xbrl_parser import (
    extract_financial_data_xbrl
)

text = run_sec_raw_ingestion(
    "Microsoft"
)

financials = (
    extract_financial_data_xbrl(
        text
    )
)

print(financials)