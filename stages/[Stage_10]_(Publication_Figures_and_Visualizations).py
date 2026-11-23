"""
[Stage_10]_(Publication_Figures_and_Visualizations).py
------------------------------------------------------
STAGE 10: Publication-Quality Figures & Visual Charts Generator.
- Generates 5 high-resolution figures in reports/figures/:
    fig1: OSRM Delay Distribution
    fig2: Top Chokepoints & SLA Breaches
    fig3: Network Topology & Bottlenecks Map
    fig4: The Graph Advantage Benchmarks
    fig5: FTL vs. Carting Economic Trade-Off
Output: reports/figures/*.png
"""

import os
import sys
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.visualize import generate_all_figures


def run_stage():
    print("=" * 75)
    print(" [STAGE 10] PUBLICATION-QUALITY FIGURES & VISUALIZATIONS GENERATOR ")
    print("=" * 75)
    t0 = time.time()
    generate_all_figures()
    print(f"\n>>> Stage 10 successfully completed in {time.time() - t0:.2f}s!")
    print(">>> Output Artifacts: reports/figures/fig[1-5]*.png")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    run_stage()
