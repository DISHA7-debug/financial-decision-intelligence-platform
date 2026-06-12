import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from state import (
    FinancialData,
    FinancialYear
)

REVENUE_TAGS = (
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "Revenues",
    "SalesRevenueNet",
)

COST_TAGS = (
    "CostOfGoodsAndServicesSold",
    "CostOfRevenue",
)

INSTANT_BALANCE_SHEET_TAGS = (
    "Assets",
    "Liabilities",
    "AssetsCurrent",
    "LiabilitiesCurrent",
    "RetainedEarningsAccumulatedDeficit",
    "LongTermDebtNoncurrent",
    "StockholdersEquity",
)


@dataclass
class XbrlContext:
    context_id: str
    has_segment: bool
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    instant: Optional[str] = None

    @property
    def is_duration(self) -> bool:
        return (
            self.start_date is not None
            and self.end_date is not None
        )

    @property
    def duration_days(self) -> Optional[int]:
        if not self.is_duration:
            return None

        start = datetime.strptime(
            self.start_date,
            "%Y-%m-%d"
        )
        end = datetime.strptime(
            self.end_date,
            "%Y-%m-%d"
        )

        return (end - start).days + 1


def _parse_contexts(
    filing_text: str
) -> Dict[str, XbrlContext]:
    contexts: Dict[str, XbrlContext] = {}

    for match in re.finditer(
        r'<context\s+id="([^"]+)"[^>]*>'
        r'(.*?)</context>',
        filing_text,
        re.DOTALL | re.IGNORECASE
    ):
        context_id = match.group(1)
        body = match.group(2)
        has_segment = (
            "<segment>" in body.lower()
        )

        start_match = re.search(
            r'<startDate>([^<]+)</startDate>',
            body,
            re.IGNORECASE
        )
        end_match = re.search(
            r'<endDate>([^<]+)</endDate>',
            body,
            re.IGNORECASE
        )
        instant_match = re.search(
            r'<instant>([^<]+)</instant>',
            body,
            re.IGNORECASE
        )

        contexts[context_id] = XbrlContext(
            context_id=context_id,
            has_segment=has_segment,
            start_date=(
                start_match.group(1)
                if start_match else None
            ),
            end_date=(
                end_match.group(1)
                if end_match else None
            ),
            instant=(
                instant_match.group(1)
                if instant_match else None
            ),
        )

    return contexts


def _find_fy_context_id(
    filing_text: str
) -> Optional[str]:
    patterns = (
        r'name="dei:DocumentFiscalPeriodFocus"'
        r'[^>]*contextRef="([^"]+)"[^>]*>\s*FY\s*<',
        r'contextRef="([^"]+)"'
        r'[^>]*name="dei:DocumentFiscalPeriodFocus"'
        r'[^>]*>\s*FY\s*<',
    )

    for pattern in patterns:
        match = re.search(
            pattern,
            filing_text,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

    return None


def _annual_context_ids(
    contexts: Dict[str, XbrlContext]
) -> list[str]:
    annual = []

    for context_id, context in contexts.items():
        if context.has_segment or not context.is_duration:
            continue

        duration_days = context.duration_days

        if (
            duration_days is not None
            and 340 <= duration_days <= 380
        ):
            annual.append(
                (context.end_date, context_id)
            )

    annual.sort(reverse=True)

    return [context_id for _, context_id in annual]


def _find_prior_fy_context_id(
    contexts: Dict[str, XbrlContext],
    current_context_id: str,
    annual_context_ids: list[str],
) -> Optional[str]:
    current = contexts.get(current_context_id)

    if current and current.is_duration:
        current_start = datetime.strptime(
            current.start_date,
            "%Y-%m-%d"
        )
        prior_end_target = (
            current_start - timedelta(days=1)
        ).strftime("%Y-%m-%d")

        for context_id, context in contexts.items():
            if context.has_segment or not context.is_duration:
                continue

            if context.end_date == prior_end_target:
                return context_id

    if current_context_id in annual_context_ids:
        index = annual_context_ids.index(
            current_context_id
        )

        if index + 1 < len(annual_context_ids):
            return annual_context_ids[index + 1]

    return None


def _find_instant_context_pair(
    contexts: Dict[str, XbrlContext],
    fy_context_id: Optional[str],
) -> Tuple[Optional[str], Optional[str]]:
    fy_context = (
        contexts.get(fy_context_id)
        if fy_context_id else None
    )

    if not fy_context or not fy_context.is_duration:
        return None, None

    current_instant_date = fy_context.end_date
    prior_instant_date = (
        datetime.strptime(
            fy_context.start_date,
            "%Y-%m-%d"
        ) - timedelta(days=1)
    ).strftime("%Y-%m-%d")

    current_context_id = None
    prior_context_id = None

    for context_id, context in contexts.items():
        if context.has_segment or context.instant is None:
            continue

        if context.instant == current_instant_date:
            current_context_id = context_id

        if context.instant == prior_instant_date:
            prior_context_id = context_id

    return current_context_id, prior_context_id


def _extract_tag_by_context(
    filing_text: str,
    tag: str,
    context_id: str,
) -> Optional[float]:
    pattern = (
        rf'<us-gaap:{tag}\b.*?'
        rf'contextRef="{re.escape(context_id)}".*?>'
        rf'\s*(-?\d+)\s*</us-gaap:{tag}>'
    )

    match = re.search(
        pattern,
        filing_text,
        re.DOTALL | re.IGNORECASE
    )

    if not match:
        return None

    return float(match.group(1)) / 1_000_000


def extract_first_two(
    filing_text: str,
    tag: str
):

    pattern = (
        rf"<us-gaap:{tag}[^>]*>"
        rf"(-?\d+)"
        rf"</us-gaap:{tag}>"
    )

    matches = re.findall(
        pattern,
        filing_text,
        re.IGNORECASE
    )

    if len(matches) >= 2:

        return (
            float(matches[0]) / 1_000_000,
            float(matches[1]) / 1_000_000
        )

    if len(matches) == 1:

        value = (
            float(matches[0]) / 1_000_000
        )

        return value, None

    return None, None


def extract_annual_tag_pair(
    filing_text: str,
    tag: str,
) -> Tuple[Optional[float], Optional[float]]:
    contexts = _parse_contexts(filing_text)
    fy_context_id = _find_fy_context_id(filing_text)
    annual_context_ids = _annual_context_ids(contexts)

    if not fy_context_id and annual_context_ids:
        fy_context_id = annual_context_ids[0]

    if not fy_context_id:
        return extract_first_two(filing_text, tag)

    prior_context_id = _find_prior_fy_context_id(
        contexts,
        fy_context_id,
        annual_context_ids,
    )

    current = _extract_tag_by_context(
        filing_text,
        tag,
        fy_context_id,
    )
    previous = None

    if prior_context_id:
        previous = _extract_tag_by_context(
            filing_text,
            tag,
            prior_context_id,
        )

    if current is None:
        return extract_first_two(filing_text, tag)

    return current, previous


def extract_instant_tag_pair(
    filing_text: str,
    tag: str,
) -> Tuple[Optional[float], Optional[float]]:
    contexts = _parse_contexts(filing_text)
    fy_context_id = _find_fy_context_id(filing_text)
    current_context_id, prior_context_id = (
        _find_instant_context_pair(
            contexts,
            fy_context_id,
        )
    )

    if not current_context_id:
        return extract_first_two(filing_text, tag)

    current = _extract_tag_by_context(
        filing_text,
        tag,
        current_context_id,
    )
    previous = None

    if prior_context_id:
        previous = _extract_tag_by_context(
            filing_text,
            tag,
            prior_context_id,
        )

    if current is None:
        return extract_first_two(filing_text, tag)

    return current, previous


def extract_annual_revenue_pair(
    filing_text: str,
) -> Tuple[Optional[float], Optional[float]]:
    for tag in REVENUE_TAGS:
        current, previous = extract_annual_tag_pair(
            filing_text,
            tag,
        )

        if current is not None:
            return current, previous

    return None, None


def extract_liabilities_pair(
    filing_text: str,
) -> Tuple[Optional[float], Optional[float]]:
    current, previous = extract_instant_tag_pair(
        filing_text,
        "Liabilities",
    )

    if current is not None:
        return current, previous

    assets_current, assets_previous = (
        extract_instant_tag_pair(
            filing_text,
            "Assets",
        )
    )
    equity_current, equity_previous = (
        extract_instant_tag_pair(
            filing_text,
            "StockholdersEquity",
        )
    )

    derived_current = None
    derived_previous = None

    if (
        assets_current is not None
        and equity_current is not None
    ):
        derived_current = assets_current - equity_current

    if (
        assets_previous is not None
        and equity_previous is not None
    ):
        derived_previous = (
            assets_previous - equity_previous
        )

    return derived_current, derived_previous


def extract_gross_profit_pair(
    filing_text: str,
) -> Tuple[Optional[float], Optional[float]]:
    current, previous = extract_annual_tag_pair(
        filing_text,
        "GrossProfit",
    )

    if current is not None:
        return current, previous

    revenue_current, revenue_previous = (
        extract_annual_revenue_pair(filing_text)
    )

    for cost_tag in COST_TAGS:
        cost_current, cost_previous = (
            extract_annual_tag_pair(
                filing_text,
                cost_tag,
            )
        )

        if (
            revenue_current is not None
            and cost_current is not None
        ):
            derived_previous = None

            if (
                revenue_previous is not None
                and cost_previous is not None
            ):
                derived_previous = (
                    revenue_previous - cost_previous
                )

            return (
                revenue_current - cost_current,
                derived_previous,
            )

    return None, None


def extract_financial_data_xbrl(
    filing_text: str
) -> FinancialData:

    revenue_current, revenue_previous = (
        extract_annual_revenue_pair(
            filing_text
        )
    )

    ocf_current, ocf_previous = (
        extract_annual_tag_pair(
            filing_text,
            "NetCashProvidedByUsedInOperatingActivities",
        )
    )

    net_income_current, net_income_previous = (
        extract_annual_tag_pair(
            filing_text,
            "NetIncomeLoss",
        )
    )

    assets_current, assets_previous = (
        extract_instant_tag_pair(
            filing_text,
            "Assets",
        )
    )

    liabilities_current, liabilities_previous = (
        extract_liabilities_pair(
            filing_text
        )
    )

    current_assets_current, current_assets_previous = (
        extract_instant_tag_pair(
            filing_text,
            "AssetsCurrent",
        )
    )

    current_liabilities_current, current_liabilities_previous = (
        extract_instant_tag_pair(
            filing_text,
            "LiabilitiesCurrent",
        )
    )

    retained_current, retained_previous = (
        extract_instant_tag_pair(
            filing_text,
            "RetainedEarningsAccumulatedDeficit",
        )
    )

    ebit_current, ebit_previous = (
        extract_annual_tag_pair(
            filing_text,
            "OperatingIncomeLoss",
        )
    )

    gross_profit_current, gross_profit_previous = (
        extract_gross_profit_pair(
            filing_text
        )
    )

    debt_current, debt_previous = (
        extract_instant_tag_pair(
            filing_text,
            "LongTermDebtNoncurrent",
        )
    )

    return FinancialData(
        current_year=FinancialYear(
            revenue=revenue_current,
            net_income=net_income_current,
            total_assets=assets_current,
            total_liabilities=liabilities_current,
            current_assets=current_assets_current,
            current_liabilities=current_liabilities_current,
            retained_earnings=retained_current,
            ebit=ebit_current,
            operating_cash_flow=ocf_current,
            long_term_debt=debt_current,
            gross_profit=gross_profit_current
        ),
        previous_year=FinancialYear(
            revenue=revenue_previous,
            net_income=net_income_previous,
            total_assets=assets_previous,
            total_liabilities=liabilities_previous,
            current_assets=current_assets_previous,
            current_liabilities=current_liabilities_previous,
            retained_earnings=retained_previous,
            ebit=ebit_previous,
            operating_cash_flow=ocf_previous,
            long_term_debt=debt_previous,
            gross_profit=gross_profit_previous
        )
    )
