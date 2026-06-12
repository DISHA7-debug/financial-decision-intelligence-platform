# Multi Agent Roadmap

## Agent 1: SEC Filing Agent

Status:
Completed

Files:
node0_sec.py
sec_downloader.py
sec_parser.py

---

## Agent 2: Financial Extraction Agent

Status:
85% Complete

Files:
node1_ingest.py
xbrl_parser.py

Remaining:
Revenue Context Selection
Operating Cash Flow
Shares Outstanding

---

## Agent 3: Risk Analysis Agent

Status:
80% Complete

Files:
node2_risk.py

Remaining:
Complete Piotroski Inputs

---

## Agent 4: Retrieval Agent

Status:
Completed

Files:
node3_rag.py
retriever.py

---

## Agent 5: Decision Agent

Status:
60% Complete

Files:
node4_decision.py
node4_rules.py

Remaining:
Hybrid Decision Engine

---

## Agent 6: Comparison Agent

Status:
Not Started

Goal:
Compare multiple companies.

Output:

Company
Revenue
Debt Ratio
Altman
Piotroski
Recommendation

---

## Agent 7: ML Risk Agent

Status:
Not Started

Goal:
Train XGBoost on company financials.

Features:
Revenue Growth
Debt Ratio
Current Ratio
Gross Margin
Altman
Piotroski
Asset Turnover

Output:
Risk Probability

---

## Agent 8: Report Agent

Status:
Not Started

Goal:
Generate Due Diligence Reports

Output:
Executive Summary
Risk Analysis
Recommendation
Supporting Evidence