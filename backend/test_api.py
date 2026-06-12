from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.api import app
from backend.schemas import (
    AnalyzeResponse,
    CommitteeReportResponse,
    CompareResponse,
    ComparisonItem,
    RankingItem,
    ReportResponse,
    RiskItem,
)
from backend.services import (
    CompanyNotFoundError,
    ModelLoadError,
    ReportNotFoundError,
    WorkflowError,
)

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@patch("backend.routers.analyze.analyze_company")
def test_analyze_success(mock_analyze):
    mock_analyze.return_value = AnalyzeResponse(
        company="Apple",
        recommendation="BUY",
        confidence="HIGH",
        altman_z=8.57,
        piotroski_f=7,
        risk_classification="Safe Zone",
        identified_risks=[
            RiskItem(
                risk="Cybersecurity Risk",
                severity="MEDIUM",
                summary="Sample summary",
                evidence="Sample evidence",
            )
        ],
        ml_recommendation="BUY",
        ml_confidence="HIGH",
    )

    response = client.post(
        "/analyze",
        json={"company": "Apple"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["company"] == "Apple"
    assert payload["recommendation"] == "BUY"
    assert payload["confidence"] == "HIGH"
    assert payload["altman_z"] == 8.57
    assert payload["piotroski_f"] == 7
    assert len(payload["identified_risks"]) == 1


@patch("backend.routers.analyze.analyze_company")
def test_analyze_unknown_company(mock_analyze):
    mock_analyze.side_effect = CompanyNotFoundError(
        "Unknown company or ticker: FakeCo"
    )

    response = client.post(
        "/analyze",
        json={"company": "FakeCo"},
    )

    assert response.status_code == 404
    assert "Unknown company" in response.json()["detail"]


@patch("backend.routers.analyze.analyze_company")
def test_analyze_workflow_failure(mock_analyze):
    mock_analyze.side_effect = WorkflowError(
        "Workflow failed for Apple: boom"
    )

    response = client.post(
        "/analyze",
        json={"company": "Apple"},
    )

    assert response.status_code == 500
    assert "Workflow failed" in response.json()["detail"]


@patch("backend.routers.analyze.analyze_company")
def test_analyze_model_failure(mock_analyze):
    mock_analyze.side_effect = ModelLoadError(
        "XGBoost model artifacts are missing"
    )

    response = client.post(
        "/analyze",
        json={"company": "Apple"},
    )

    assert response.status_code == 503


@patch("backend.routers.compare.compare_companies_api")
def test_compare_success(mock_compare):
    mock_compare.return_value = CompareResponse(
        ranking=[
            RankingItem(
                rank=1,
                company="Apple",
                recommendation="BUY",
                ml_recommendation="BUY",
                altman_z=8.57,
                piotroski_f=7,
                risk_classification="Safe Zone",
            ),
            RankingItem(
                rank=2,
                company="Microsoft",
                recommendation="HOLD",
                ml_recommendation="HOLD",
                altman_z=8.31,
                piotroski_f=5,
                risk_classification="Safe Zone",
            ),
        ],
        comparison=[
            ComparisonItem(
                company="Apple",
                revenue=416161.0,
                rule_recommendation="BUY",
                rank=1,
            ),
            ComparisonItem(
                company="Microsoft",
                revenue=281724.0,
                rule_recommendation="HOLD",
                rank=2,
            ),
        ],
    )

    response = client.post(
        "/compare",
        json={
            "companies": ["Apple", "Microsoft"],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["ranking"]) == 2
    assert payload["ranking"][0]["company"] == "Apple"
    assert payload["ranking"][0]["rank"] == 1
    assert len(payload["comparison"]) == 2


@patch("backend.routers.reports.get_company_report")
def test_company_report_success(mock_report):
    mock_report.return_value = ReportResponse(
        company="Apple",
        report_path="reports/apple_report.txt",
        content="DUE DILIGENCE REPORT\n...",
    )

    response = client.get("/report/Apple")

    assert response.status_code == 200
    payload = response.json()
    assert payload["company"] == "Apple"
    assert "DUE DILIGENCE REPORT" in payload["content"]


@patch("backend.routers.reports.get_company_report")
def test_company_report_not_found(mock_report):
    mock_report.side_effect = ReportNotFoundError(
        "No report found for FakeCo"
    )

    response = client.get("/report/FakeCo")

    assert response.status_code == 404


@patch("backend.routers.reports.get_committee_report")
def test_committee_report_success(mock_report):
    mock_report.return_value = CommitteeReportResponse(
        report_path="reports/investment_committee_report.txt",
        content="INVESTMENT COMMITTEE REPORT\n...",
    )

    response = client.get("/committee-report")

    assert response.status_code == 200
    assert "INVESTMENT COMMITTEE REPORT" in response.json()["content"]


@patch("backend.routers.reports.get_committee_report")
def test_committee_report_missing(mock_report):
    mock_report.side_effect = ReportNotFoundError(
        "Investment committee report has not been generated yet."
    )

    response = client.get("/committee-report")

    assert response.status_code == 404


def test_openapi_docs_available():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/analyze" in response.json()["paths"]
    assert "/compare" in response.json()["paths"]
    assert "/health" in response.json()["paths"]
