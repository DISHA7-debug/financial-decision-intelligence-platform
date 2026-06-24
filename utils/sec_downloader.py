from sec_edgar_downloader import Downloader


def download_latest_10k(
    ticker: str
):

    print(f"Starting SEC download for {ticker}")

    dl = Downloader(
        "FinancialDueDiligenceAgent",
        "dishaworks07@gmail.com",
        "data/sec_filings"
    )

    dl.get(
        "10-K",
        ticker,
        limit=1
    )

    print(f"Finished SEC download for {ticker}")