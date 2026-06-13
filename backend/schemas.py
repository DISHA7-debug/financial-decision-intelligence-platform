from pydantic import BaseModel, Field


class RiskItem(BaseModel):
    risk: str
    severity: str
    summary: str
    evidence: str


class AnalyzeRequest(BaseModel):
    company: str = Field(
        ...,
        min_length=1,
        examples=["Apple"],
    )


class AnalyzeResponse(BaseModel):
    company: str
    recommendation: str
    confidence: str
    altman_z: float | None = None
    piotroski_f: int | None = None
    revenue: float | None = None
    net_income: float | None = None
    gross_margin: float | None = None
    current_ratio: float | None = None
    risk_classification: str | None = None
    identified_risks: list[RiskItem] = Field(default_factory=list)
    ml_recommendation: str | None = None
    ml_confidence: str | None = None


class CompareRequest(BaseModel):
    companies: list[str] = Field(
        ...,
        min_length=1,
        examples=[["Apple", "Microsoft", "Nvidia"]],
    )


class RankingItem(BaseModel):
    rank: int
    company: str
    revenue: float | None = None
    growth: float | None = None
    recommendation: str | None = None
    ml_recommendation: str | None = None
    altman_z: float | None = None
    piotroski_f: int | None = None
    risk_classification: str | None = None


class ComparisonItem(BaseModel):
    company: str
    revenue: float | None = None
    revenue_growth: float | None = None
    net_income: float | None = None
    current_ratio: float | None = None
    debt_ratio: float | None = None
    altman_z: float | None = None
    piotroski_f: int | None = None
    risk_classification: str | None = None
    rule_recommendation: str | None = None
    ml_recommendation: str | None = None
    rank: int | None = None


class CompareResponse(BaseModel):
    ranking: list[RankingItem]
    comparison: list[ComparisonItem]


class ReportResponse(BaseModel):
    company: str
    report_path: str
    content: str


class CommitteeReportResponse(BaseModel):
    report_path: str
    content: str


class HealthResponse(BaseModel):
    status: str


class ErrorResponse(BaseModel):
    detail: str
