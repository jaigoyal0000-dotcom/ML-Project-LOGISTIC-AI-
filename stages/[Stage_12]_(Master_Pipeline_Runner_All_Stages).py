"""
[Stage_12]_(Master_Pipeline_Runner_All_Stages).py
-------------------------------------------------
STAGE 12: Master Execution Orchestrator.
Sequentially runs all 11 stages from raw data ingestion to master PDF report generation.
"""

import os
import sys
import time
import importlib

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def run_all_stages():
    print("\n" + "=" * 80)
    print("  DELHIVERY NETWORK INTELLIGENCE: COMPLETE STAGE-WISE PIPELINE RUNNER  ")
    print("=" * 80)
    start_time = time.time()

    stages = [
        ("[Stage 01] Data Ingestion & Preprocessing", "stages.[Stage_01]_(Data_Ingestion_and_Preprocessing)"),
        ("[Stage 02] Network Graph Construction & Centrality", "stages.[Stage_02]_(Network_Graph_Construction_and_Centrality)"),
        ("[Stage 03] Geospatial Facility Mapping", "stages.[Stage_03]_(Geospatial_Mapping_and_Coordinates)"),
        ("[Stage 04] Node2Vec Embeddings & Graph Features", "stages.[Stage_04]_(Node2Vec_Embeddings_and_Neighborhood_Features)"),
        ("[Stage 05] ML Modeling & Benchmarking", "stages.[Stage_05]_(Baseline_vs_Graph_ML_Benchmarking)"),
        ("[Stage 06] Deep PyG GraphSAGE GNN", "stages.[Stage_06]_(Deep_GraphSAGE_GNN_PyTorch_Geometric)"),
        ("[Stage 07] FTL vs. Carting Decision Framework", "stages.[Stage_07]_(FTL_vs_Carting_Route_Type_Decision_Framework)"),
        ("[Stage 08] Operations Strategy Memo & ROI", "stages.[Stage_08]_(Operations_Strategy_Memo_and_ROI_Simulation)"),
        ("[Stage 09] Dynamic Congestion Bypass Router", "stages.[Stage_09]_(Dynamic_Congestion_Bypass_Router)"),
        ("[Stage 10] Publication Visualizations", "stages.[Stage_10]_(Publication_Figures_and_Visualizations)"),
        ("[Stage 11] Master PDF Report Builder", "stages.[Stage_11]_(Executive_Master_PDF_Report_Builder)")
    ]

    for title, mod_name in stages:
        print(f"\n>>> EXECUTING {title}...")
        mod = importlib.import_module(mod_name)
        mod.run_stage()

    total_time = time.time() - start_time
    print("\n" + "=" * 80)
    print(f"  >>> ALL 11 STAGES COMPLETED WITH 100% SUCCESS IN {total_time:.1f} SECONDS! <<<  ")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_all_stages()
