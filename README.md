# Financial Decision Intelligence Platform

An AI-powered platform that analyzes SEC filings, extracts financial intelligence, identifies business risks, generates investment recommendations, and compares multiple companies.

## Features

- SEC 10-K ingestion
- XBRL financial extraction
- Altman Z-Score analysis
- Piotroski F-Score analysis
- SEC risk retrieval
- Risk intelligence categorization
- Rule-based recommendations
- XGBoost predictions
- Due diligence reports
- Investment committee reports
- **FastAPI REST API** for frontend integration

## Tech Stack

- Python
- FastAPI + Uvicorn
- FAISS
- Sentence Transformers
- XGBoost
- Gemini
- SEC EDGAR

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## CLI Usage

```bash
python workflow.py Apple
python report_generator.py Apple
python compare_report.py Apple Microsoft Nvidia Tesla Amazon
```

## API Server

Start the API from the project root:

```bash
source venv/bin/activate
uvicorn backend.api:app --reload
```

Open Swagger UI:

http://127.0.0.1:8000/docs

Health check:

http://127.0.0.1:8000/health

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service health check |
| POST | `/analyze` | Run full due diligence on one company |
| POST | `/compare` | Compare and rank multiple companies |
| GET | `/report/{company}` | Return due diligence report text |
| GET | `/committee-report` | Return latest investment committee report |

### POST `/analyze`

Request:

```json
{
  "company": "Apple"
}
```

Response:

```json
{
  "company": "Apple",
  "recommendation": "BUY",
  "confidence": "HIGH",
  "altman_z": 8.57,
  "piotroski_f": 7,
  "risk_classification": "Safe Zone",
  "identified_risks": [
    {
      "risk": "Cybersecurity Risk",
      "severity": "MEDIUM",
      "summary": "...",
      "evidence": "..."
    }
  ],
  "ml_recommendation": "BUY",
  "ml_confidence": "HIGH"
}
```

### POST `/compare`

Request:

```json
{
  "companies": ["Apple", "Microsoft", "Nvidia"]
}
```

Response:

```json
{
  "ranking": [
    {
      "rank": 1,
      "company": "Apple",
      "recommendation": "BUY",
      "ml_recommendation": "BUY",
      "altman_z": 8.57,
      "piotroski_f": 7,
      "risk_classification": "Safe Zone"
    }
  ],
  "comparison": [
    {
      "company": "Apple",
      "revenue": 416161.0,
      "revenue_growth": 0.064,
      "net_income": 112010.0,
      "current_ratio": 0.89,
      "debt_ratio": 0.795,
      "altman_z": 8.57,
      "piotroski_f": 7,
      "risk_classification": "Safe Zone",
      "rule_recommendation": "BUY",
      "ml_recommendation": "BUY",
      "rank": 1
    }
  ]
}
```

### Example curl commands

```bash
curl http://127.0.0.1:8000/health

curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"company": "Apple"}'

curl -X POST http://127.0.0.1:8000/compare \
  -H "Content-Type: application/json" \
  -d '{"companies": ["Apple", "Microsoft", "Nvidia"]}'

curl http://127.0.0.1:8000/report/Apple

curl http://127.0.0.1:8000/committee-report
```

## API Tests

```bash
source venv/bin/activate
python -m pytest backend/test_api.py -v
```

## Error Responses

| Status | Meaning |
|--------|---------|
| 404 | Unknown company or missing report |
| 500 | Workflow or unexpected server error |
| 503 | XGBoost model loading failure |
