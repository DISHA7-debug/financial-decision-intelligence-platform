# Current Codebase Status

## node0_sec.py

Purpose:
SEC Filing Agent

Status:
Working

Responsibilities:
- Download latest 10-K
- Store filing locally
- Return raw filing text

---

## node1_ingest.py

Purpose:
Financial Extraction Agent

Status:
Working

Responsibilities:
- Parse raw SEC filing
- Extract FinancialData object
- Cache extracted financials

Current Backend:
XBRL Parser

Removed:
PDF Extraction
Gemini Extraction

Remaining:
Improve context selection

---

## node2_risk.py

Purpose:
Risk Analysis Agent

Status:
Working

Calculations:
- Altman Z Score
- Piotroski F Score

Remaining:
- Improve handling of missing fields
- Use Operating Cash Flow when available

---

## node3_rag.py

Purpose:
Retrieval Agent

Status:
Working

Responsibilities:
- Query SEC Vector DB
- Retrieve risk-related context

Backend:
FAISS
all-MiniLM-L6-v2

---

## node4_decision.py

Purpose:
Decision Agent

Status:
Partially Working

Issues:
- LLM recommendations often inconsistent

Example:
Altman Safe Zone
Piotroski Average
Recommendation = AVOID

Needs:
Deterministic decision layer

---

## node4_rules.py

Purpose:
Rule-based fallback

Status:
Needs improvement

Target Logic:

BUY:
Altman > 3
Piotroski >= 7

HOLD:
Altman > 3
Piotroski >= 4

AVOID:
Otherwise