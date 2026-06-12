from nodes.node0_sec import (
    run_sec_raw_ingestion
)

from utils.xbrl_parser import (
    extract_financial_data_xbrl
)


def _load_filing(company: str) -> str:
    return run_sec_raw_ingestion(company)


def _assert_core_fields(financials, company: str) -> None:
    current = financials.current_year

    assert current.revenue is not None, company
    assert current.net_income is not None, company
    assert current.total_assets is not None, company
    assert current.total_liabilities is not None, company
    assert current.gross_profit is not None, company


def test_apple_annual_revenue():
    text = _load_filing("Apple")
    financials = extract_financial_data_xbrl(text)

    _assert_core_fields(financials, "Apple")

    assert financials.previous_year.revenue is not None

    # FY2025 consolidated net sales (10-K filed Sep 2025)
    assert 410_000 <= financials.current_year.revenue <= 420_000
    assert 385_000 <= financials.previous_year.revenue <= 395_000

    print(
        "Apple revenue:",
        financials.current_year.revenue,
        financials.previous_year.revenue,
    )


def test_apple_operating_cash_flow():
    text = _load_filing("Apple")
    financials = extract_financial_data_xbrl(text)

    assert financials.current_year.operating_cash_flow is not None
    assert financials.previous_year.operating_cash_flow is not None

    # FY2025 / FY2024 cash from operations (millions USD)
    assert 100_000 <= financials.current_year.operating_cash_flow <= 120_000
    assert 100_000 <= financials.previous_year.operating_cash_flow <= 125_000

    print(
        "Apple operating cash flow:",
        financials.current_year.operating_cash_flow,
        financials.previous_year.operating_cash_flow,
    )


def test_microsoft_operating_cash_flow():
    text = _load_filing("Microsoft")
    financials = extract_financial_data_xbrl(text)

    assert financials.current_year.operating_cash_flow is not None
    assert financials.previous_year.operating_cash_flow is not None

    # FY2025 / FY2024 net cash from operations (millions USD)
    assert financials.current_year.operating_cash_flow >= 100_000
    assert financials.previous_year.operating_cash_flow >= 100_000

    print(
        "Microsoft operating cash flow:",
        financials.current_year.operating_cash_flow,
        financials.previous_year.operating_cash_flow,
    )


def test_microsoft_annual_revenue():
    text = _load_filing("Microsoft")
    financials = extract_financial_data_xbrl(text)

    _assert_core_fields(financials, "Microsoft")

    assert financials.previous_year.revenue is not None

    # FY2025 consolidated revenue (fiscal year ended Jun 2025)
    assert financials.current_year.revenue >= 245_000
    assert financials.previous_year.revenue >= 210_000

    # Guard against segment-level product revenue (~64B)
    assert financials.current_year.revenue > 200_000
    assert financials.previous_year.revenue > 200_000

    print(
        "Microsoft revenue:",
        financials.current_year.revenue,
        financials.previous_year.revenue,
    )


def test_nvidia_annual_revenue():
    text = _load_filing("Nvidia")
    financials = extract_financial_data_xbrl(text)

    _assert_core_fields(financials, "Nvidia")

    assert financials.previous_year.revenue is not None

    # FY2026 consolidated revenue (fiscal year ended Jan 2026)
    assert financials.current_year.revenue >= 150_000
    assert financials.previous_year.revenue >= 100_000

    print(
        "Nvidia revenue:",
        financials.current_year.revenue,
        financials.previous_year.revenue,
    )


def test_tesla_core_financials():
    text = _load_filing("Tesla")
    financials = extract_financial_data_xbrl(text)

    _assert_core_fields(financials, "Tesla")

    assert financials.current_year.revenue >= 80_000

    print(
        "Tesla revenue:",
        financials.current_year.revenue,
        financials.current_year.total_liabilities,
    )


def test_amazon_core_financials():
    text = _load_filing("Amazon")
    financials = extract_financial_data_xbrl(text)

    _assert_core_fields(financials, "Amazon")

    assert financials.current_year.revenue >= 600_000
    assert financials.current_year.total_liabilities is not None
    assert financials.current_year.total_assets is not None
    assert (
        financials.current_year.total_liabilities
        < financials.current_year.total_assets
    )

    print(
        "Amazon revenue:",
        financials.current_year.revenue,
        "liabilities:",
        financials.current_year.total_liabilities,
        "gross_profit:",
        financials.current_year.gross_profit,
    )


if __name__ == "__main__":
    test_apple_annual_revenue()
    test_microsoft_annual_revenue()
    test_nvidia_annual_revenue()
    test_tesla_core_financials()
    test_amazon_core_financials()
    test_apple_operating_cash_flow()
    test_microsoft_operating_cash_flow()
    print("All XBRL validation tests passed.")
