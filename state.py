from pydantic import BaseModel
from typing import Optional


class FinancialYear(BaseModel):
    revenue: float | None = None
    net_income: float | None = None

    total_assets: float | None = None
    total_liabilities: float | None = None

    current_assets: float | None = None
    current_liabilities: float | None = None

    retained_earnings: float | None = None
    ebit: float | None = None

    operating_cash_flow: float | None = None
    long_term_debt: float | None = None
    gross_profit: float | None = None
    shares_outstanding: float | None = None

class FinancialData(BaseModel):
    current_year: FinancialYear
    previous_year: FinancialYear



class RiskMetrics(BaseModel):
    altman_z_score: Optional[float] = None
    piotroski_f_score: Optional[int] = None
    risk_classification: Optional[str] = None


class DecisionOutput(BaseModel):
    recommendation: Optional[str] = None
    confidence: Optional[str] = None
    memo: Optional[str] = None

class AgentState(BaseModel):
    company_name: str

    financial_data: Optional[
        FinancialData
    ] = None

    risk_metrics: Optional[
        RiskMetrics
    ] = None

    retrieved_context: Optional[
        str
    ] = None

    decision_output: Optional[
        DecisionOutput
    ] = None