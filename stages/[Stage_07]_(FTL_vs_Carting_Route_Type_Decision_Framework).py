"""
[Stage_07]_(FTL_vs_Carting_Route_Type_Decision_Framework).py
------------------------------------------------------------
STAGE 7: Empirical Route-Type Optimization (FTL vs. Carting).
- Implements mathematical cost and time trade-off models:
    Cost_FTL(d) = INR 38/km * d
    Cost_Carting(d, h) = INR 22/km * d + INR 350 * h
- Computes breakeven distance D* = 21.875 * h km.
- Generates 4-rule automated dispatch decision matrix.
Output: data/ftl_vs_carting_rules.csv
"""

import os
import sys
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.decision_framework import run_decision_framework


def run_stage():
    print("=" * 75)
    print(" [STAGE 07] FTL VS. CARTING ROUTE-TYPE DECISION FRAMEWORK ")
    print("=" * 75)
    t0 = time.time()
    rules_df = run_decision_framework()
    print(f"\n>>> Stage 07 successfully completed in {time.time() - t0:.2f}s!")
    print(">>> Output Artifact: data/ftl_vs_carting_rules.csv")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    run_stage()
