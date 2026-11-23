"""
[Stage_08]_(Operations_Strategy_Memo_and_ROI_Simulation).py
-----------------------------------------------------------
STAGE 8: Operations Strategy Memo & Capital Upgrade ROI Simulation.
- Simulates modernizing the Top 3 Chokepoint Hubs (Gurgaon, Bangalore, Bhiwandi).
- Quantifies 7.01% network-wide reduction in late deliveries.
- Calculates INR 32,406,400 (INR 3.24 Crores) in annualized revenue-at-risk recovered.
Outputs: reports/operations_strategy_memo.md, reports/strategy_impact_metrics.json
"""

import os
import sys
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.strategy_memo import StrategyMemoGenerator


def run_stage():
    print("=" * 75)
    print(" [STAGE 08] OPERATIONS STRATEGY MEMO & CAPITAL UPGRADE ROI MODEL ")
    print("=" * 75)
    t0 = time.time()
    gen = StrategyMemoGenerator()
    gen.run_and_save()
    print(f"\n>>> Stage 08 successfully completed in {time.time() - t0:.2f}s!")
    print(">>> Output Artifacts: reports/operations_strategy_memo.md, reports/strategy_impact_metrics.json")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    run_stage()
