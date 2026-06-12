EXTRACTION_PROMPT = """
You are a financial analyst.

Extract financial metrics for BOTH the latest fiscal year and the immediately previous fiscal year.

Return ONLY valid JSON.

{{
    "current_year": {{
        "revenue": null,
        "net_income": null,
        "total_assets": null,
        "total_liabilities": null,
        "current_assets": null,
        "current_liabilities": null,
        "retained_earnings": null,
        "ebit": null
        "operating_cash_flow": null,
        "long_term_debt": null,
        "gross_profit": null,
        "shares_outstanding": null
    }},
    "previous_year": {{
        "revenue": null,
        "net_income": null,
        "total_assets": null,
        "total_liabilities": null,
        "current_assets": null,
        "current_liabilities": null,
        "retained_earnings": null,
        "ebit": null
        "operating_cash_flow": null,
        "long_term_debt": null,
        "gross_profit": null,
        "shares_outstanding": null
    }}
}}

Rules:

1. Use the latest fiscal year as current_year.
2. Use the immediately preceding fiscal year as previous_year.
3. Use Operating Income as EBIT if EBIT is not explicitly stated.
4. Use Accumulated Deficit or Retained Earnings when available.
5. Return numbers only.
6. Do not include currency symbols.
7. Do not include explanations.
8. Return valid JSON only.
9. Use Net Cash Provided by Operating Activities for operating_cash_flow.

10. Use Term Debt or Long-Term Debt for long_term_debt.

11. Use Gross Margin amount as gross_profit when available.
Otherwise calculate:
Revenue - Cost of Sales.

12. Use weighted average shares outstanding or issued shares outstanding for shares_outstanding.

Financial Statements:

{context}
"""