import json
import os

from state import FinancialData

from utils.xbrl_parser import (
    extract_financial_data_xbrl
)

CACHE_VERSION = 2


def _is_cache_usable(
    data: dict
) -> bool:
    if data.get("_cache_version") != CACHE_VERSION:
        return False

    current_year = data.get("current_year", {})

    if current_year.get("revenue") is None:
        return False

    if (
        current_year.get("total_assets") is not None
        and current_year.get("total_liabilities") is None
    ):
        return False

    return True


def _financial_data_from_cache(
    data: dict
) -> FinancialData:
    payload = {
        key: value
        for key, value in data.items()
        if key != "_cache_version"
    }

    return FinancialData.model_validate(payload)


def _write_cache(
    cache_file: str,
    financial_data: FinancialData
) -> None:

    os.makedirs(
        os.path.dirname(cache_file),
        exist_ok=True
    )

    with open(
        cache_file,
        "w"
    ) as f:
        json.dump(
            {
                "_cache_version": CACHE_VERSION,
                **financial_data.model_dump(),
            },
            f,
            indent=4
        )


def run_ingestion_from_text(
    text: str,
    cache_key: str
) -> FinancialData:

    cache_file = (
        f"data/cache/{cache_key}.json"
    )

    if os.path.exists(cache_file):
        with open(
            cache_file,
            "r"
        ) as f:
            cached_data = json.load(f)

        if _is_cache_usable(cached_data):
            print(
                "\nLoading financials from cache...\n"
            )

            return _financial_data_from_cache(cached_data)

        print(
            "\nCache stale or incomplete. "
            "Running XBRL extraction...\n"
        )
    else:
        print(
            "\nNo cache found. Running XBRL extraction...\n"
        )

    financial_data = (
        extract_financial_data_xbrl(
            text
        )
    )

    _write_cache(
        cache_file,
        financial_data
    )

    print(
        "\nFinancials cached successfully.\n"
    )

    return financial_data


if __name__ == "__main__":

    from nodes.node0_sec import (
        run_sec_raw_ingestion
    )

    filing_text = (
        run_sec_raw_ingestion(
            "Apple"
        )
    )

    result = (
        run_ingestion_from_text(
            filing_text,
            "apple"
        )
    )

    print(result)
