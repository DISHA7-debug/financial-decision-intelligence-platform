# Financial Decision Intelligence Platform

> AI-powered multi-agent financial due diligence system that transforms SEC filings into structured investment intelligence.

🌐 **Live Demo:** https://financial-decision-intelligence-pla.vercel.app/

---

## Overview

Financial analysts spend hours reviewing SEC filings, financial statements, risk disclosures, and company reports before making investment decisions.

The Financial Decision Intelligence Platform automates large parts of this workflow by combining retrieval systems, financial analytics, machine learning, and agent-based decision pipelines.

Instead of manually processing hundreds of pages of disclosures, users can generate structured company analyses, compare investment opportunities, identify risks, and produce committee-ready reports in seconds.

---

## Key Features

### SEC Filing Intelligence

* Automated SEC 10-K filing retrieval
* Regulatory disclosure processing
* Financial statement extraction
* Structured financial data generation

### Financial Analysis

* Revenue and profitability analysis
* Liquidity assessment
* Solvency evaluation
* Asset utilization metrics
* Growth trend analysis

### Risk Intelligence

* Altman Z-Score calculation
* Piotroski F-Score evaluation
* Semantic risk retrieval
* Disclosure-based risk identification
* Risk classification engine

### Investment Decision Engine

* Rule-based investment recommendations
* XGBoost-powered prediction model
* Confidence scoring
* Buy / Hold / Avoid classification

### Portfolio Comparison

* Multi-company analysis
* Side-by-side comparisons
* Ranking engine
* Investment committee support

### Report Generation

* Company due diligence reports
* Investment committee reports
* Structured decision summaries
* AI-assisted investment memos

---

# System Architecture

The platform follows a multi-stage agentic workflow where each component specializes in a specific financial analysis task.

```text
SEC Filing Agent
        │
        ▼
Financial Extraction Agent
        │
        ▼
Risk Intelligence Agent
        │
        ▼
Investment Decision Agent
        │
        ▼
Report Generation Agent
```

### Agent Responsibilities

#### SEC Filing Agent

Responsible for:

* Retrieving SEC filings
* Managing filing ingestion
* Processing raw regulatory disclosures

#### Financial Extraction Agent

Responsible for:

* Parsing financial statements
* Extracting structured metrics
* Building financial datasets

#### Risk Intelligence Agent

Responsible for:

* Risk scoring
* Financial health assessment
* Semantic retrieval of disclosures

#### Investment Decision Agent

Responsible for:

* Recommendation generation
* Confidence scoring
* Investment classification

#### Report Generation Agent

Responsible for:

* Due diligence reports
* Committee-ready summaries
* Decision explanations

---

# Technology Stack

## Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS
* Framer Motion

## Backend

* FastAPI
* Python

## AI & Machine Learning

* Gemini
* Sentence Transformers
* FAISS
* XGBoost

## Financial Data

* SEC EDGAR
* XBRL Processing

## Deployment

* Vercel
* Railway

---

# Workflow

```text
User Request
      │
      ▼
SEC Filing Retrieval
      │
      ▼
Financial Extraction
      │
      ▼
Risk Analysis
      │
      ▼
Semantic Retrieval
      │
      ▼
Investment Recommendation
      │
      ▼
Report Generation
```

---

# Example Use Cases

### Company Analysis

Analyze a single company and receive:

* Financial metrics
* Risk assessment
* Investment recommendation
* AI-generated explanation

### Portfolio Comparison

Compare multiple companies and receive:

* Relative rankings
* Financial comparison
* Investment committee insights

### Due Diligence

Generate structured investment reports directly from SEC filings.

---

# API Endpoints

## Analyze Company

```http
POST /analyze
```

Request:

```json
{
  "company": "Apple"
}
```

---

## Compare Companies

```http
POST /compare
```

Request:

```json
{
  "companies": [
    "Apple",
    "Microsoft",
    "NVIDIA"
  ]
}
```

---

## Generate Company Report

```http
GET /report/{company}
```

---

## Health Check

```http
GET /health
```

---

# Local Setup

Clone the repository:

```bash
git clone https://github.com/DISHA7-debug/financial-decision-intelligence-platform.git
cd financial-decision-intelligence-platform
```

Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Backend:

```bash
uvicorn backend.api:app --reload
```

---

# Environment Variables

Backend:

```env
GEMINI_API_KEY=your_api_key
```

Frontend:

```env
NEXT_PUBLIC_API_BASE_URL=https://financial-decision-intelligence-platform-production.up.railway.app
```

---

# Future Improvements

* Real-time market data integration
* Multi-filing historical analysis
* Earnings call intelligence
* Multi-agent orchestration framework
* Institutional portfolio optimization
* Explainable AI recommendations
* Advanced financial forecasting

---

# Project Highlights

* Multi-Agent Financial Intelligence System
* SEC Filing Retrieval & Processing
* Financial Risk Analytics
* Semantic Retrieval Pipeline
* XGBoost Recommendation Engine
* Automated Investment Research
* Production Deployment on Railway & Vercel

---

## Live Demo

🚀 https://financial-decision-intelligence-pla.vercel.app/

---

Built with a focus on Financial AI, Decision Intelligence, Retrieval Systems, and Agentic Workflows.
