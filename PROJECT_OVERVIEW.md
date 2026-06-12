# Financial Due Diligence Agent

## Goal

Build a multi-agent financial due diligence system that:

1. Downloads SEC filings automatically
2. Extracts financial metrics
3. Computes risk scores
4. Retrieves business risks from filings
5. Generates investment recommendations
6. Compares companies
7. Trains ML models for risk prediction
8. Produces due diligence reports

---

## Current Architecture

Company Name
↓
SEC Filing Agent
↓
XBRL Extraction Agent
↓
Risk Analysis Agent
↓
Retrieval Agent
↓
Decision Agent
↓
Report Generation Agent

---

## Core Technologies

Python
FAISS
Sentence Transformers
SEC EDGAR
Pydantic
Gemini
XGBoost (planned)

---

## Current Status

Workflow executes end-to-end.

Working:

- SEC Download
- Filing Parsing
- XBRL Extraction
- Altman Z Score
- Piotroski Score
- RAG Retrieval
- Decision Generation
- Rule Fallback

Not Finished:

- Revenue context selection
- Operating Cash Flow extraction
- Shares Outstanding extraction
- Comparison Agent
- XGBoost Agent
- Report Agent