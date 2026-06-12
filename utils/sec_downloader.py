from sec_edgar_downloader import Downloader


def download_latest_10k(
    ticker: str
):

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

    print(
        f"Downloaded latest 10-K for {ticker}"
    )