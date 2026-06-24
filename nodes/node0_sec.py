import os

from utils.sec_parser import (
    extract_main_10k
)

from utils.sec_downloader import (
    download_latest_10k
)
from utils.sec_parser import (
    load_raw_filing
)


COMPANY_TO_TICKER = {
    "APPLE": "AAPL",
    "MICROSOFT": "MSFT",
    "NVIDIA": "NVDA",
    "TESLA": "TSLA",
    "AMAZON": "AMZN"
}

TICKERS = {
    "AAPL",
    "MSFT",
    "NVDA",
    "TSLA",
    "AMZN"
}


def resolve_ticker(
    company_or_ticker: str
):

    value = company_or_ticker.upper()

    if value in TICKERS:
        return value

    return COMPANY_TO_TICKER[value]


def run_sec_ingestion(
    company_name: str
) -> str:

    ticker = resolve_ticker(
        company_name
    )

    base_path = (
        f"data/sec_filings/"
        f"sec-edgar-filings/"
        f"{ticker}/10-K"
    )

    if not os.path.exists(base_path):

        print(
            f"\nDownloading filing for {ticker}...\n"
        )

        download_latest_10k(
            ticker
        )

        # recompute path after download
        if not os.path.exists(base_path):
            raise FileNotFoundError(
                f"SEC filing download failed for {ticker}"
            )

    folders = sorted(
        os.listdir(base_path)
    )

    latest_folder = folders[-1]

    filing_path = os.path.join(
        base_path,
        latest_folder,
        "full-submission.txt"
    )

    filing_text = (
        extract_main_10k(
            filing_path
        )
    )

    return filing_text


def run_sec_raw_ingestion(
    company_name: str
) -> str:

    ticker = resolve_ticker(
        company_name
    )

    base_path = (
        f"data/sec_filings/"
        f"sec-edgar-filings/"
        f"{ticker}/10-K"
    )

    folders = sorted(
        os.listdir(base_path)
    )

    latest_folder = folders[-1]

    filing_path = os.path.join(
        base_path,
        latest_folder,
        "full-submission.txt"
    )

    return load_raw_filing(
        filing_path
    )