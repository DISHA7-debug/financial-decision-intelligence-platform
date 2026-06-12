# Immediate Next Tasks

Priority 1

Fix XBRL Revenue Extraction

Problem:
Microsoft revenue extracted incorrectly.

Expected:
Annual revenue context.

File:
utils/xbrl_parser.py

---

Priority 2

Extract Operating Cash Flow

Add support for:

NetCashProvidedByUsedInOperatingActivities

File:
utils/xbrl_parser.py

---

Priority 3

Extract Shares Outstanding

Add support for:

CommonStockSharesOutstanding

EntityCommonStockSharesOutstanding

File:
utils/xbrl_parser.py

---

Priority 4

Improve Rule Engine

File:
node4_rules.py

Implement:

BUY:
Altman > 3
Piotroski >= 7

HOLD:
Altman > 3
Piotroski >= 4

AVOID:
Otherwise

---

Priority 5

Make Rule Engine Primary

Current:
LLM First

Target:
Rules First
LLM Generates Explanation Only

File:
workflow.py
node4_decision.py