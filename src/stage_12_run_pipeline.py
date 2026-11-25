"""
src/stage_12_run_pipeline.py
----------------------------
End-to-End Master Pipeline Runner for Delhivery Logistics Network Intelligence.
Executes all 11 stages chronologically:
  Stage 01: Data Ingestion & Preprocessing
  Stage 02: Network Graph Construction & Centrality Audit
  Stage 03: Geospatial Hub Mapping
  Stage 04: Node2Vec Embeddings & GraphSAGE Features
  Stage 05: Baseline vs. Graph-Enhanced ML Benchmarking
  Stage 06: Deep GraphSAGE GNN (PyTorch Geometric)
  Stage 07: FTL vs. Carting Decision Framework
  Stage 08: Operations Strategy Memo & ROI Simulation
  Stage 09: Dynamic Congestion Bypass Router Validation
  Stage 10: Publication-Quality Figures Generation
  Stage 11: Master Executive PDF Report Compilation
"""

import time
from src.stage_01_data_prep import prepare_and_save_data
from src.stage_02_graph_builder import run_graph_pipeline
from src.stage_03_geo_mapper import enrich_hubs_with_geocoordinates
from src.stage_04_node_embeddings import run_embedding_pipeline
from src.stage_05_models import run_modeling_pipeline
from src.stage_06_gnn_graphsage import run_gnn_pipeline
from src.stage_07_decision_framework import run_decision_framework
from src.stage_08_strategy_memo import StrategyMemoGenerator
from src.stage_09_route_optimizer import DynamicRouteOptimizer
from src.stage_10_visualize import generate_all_figures
from src.stage_11_report_pdf import build_master_pdf


def main():
    print("=" * 72)
    print("  DELHIVERY NETWORK INTELLIGENCE: END-TO-END STAGE PIPELINE RUNNER  ")
    print("=" * 72)
    start_time = time.time()

    print("\n[STAGE 01/11] Data Ingestion & Preprocessing...")
    prepare_and_save_data()

    print("\n[STAGE 02/11] Building Directed Weighted Network Graph & Chokepoint Audit...")
    run_graph_pipeline()

    print("\n[STAGE 03/11] Geocoding Logistics Facilities Across India...")
    enrich_hubs_with_geocoordinates()

    print("\n[STAGE 04/11] Generating Node2Vec Embeddings & GraphSAGE Features...")
    run_embedding_pipeline()

    print("\n[STAGE 05/11] Training & Benchmarking Baseline vs. Graph-Enhanced ETA Models...")
    run_modeling_pipeline()

    print("\n[STAGE 06/11] Training Deep PyTorch Geometric GraphSAGE GNN...")
    run_gnn_pipeline()

    print("\n[STAGE 07/11] Building FTL vs. Carting Route-Type Decision Framework...")
    run_decision_framework()

    print("\n[STAGE 08/11] Generating Executive Strategy Memo & ROI Model...")
    StrategyMemoGenerator().run_and_save()

    print("\n[STAGE 09/11] Validating Dynamic Congestion Bypass Router...")
    opt = DynamicRouteOptimizer()
    opt.load_network()
    opt.find_routes("IND000000ACB", "IND562132AAA")

    print("\n[STAGE 10/11] Generating High-Resolution Publication Charts...")
    generate_all_figures()

    print("\n[STAGE 11/11] Compiling Master Executive PDF Project Report...")
    build_master_pdf()

    total_duration = time.time() - start_time
    print("\n" + "=" * 72)
    print(f" ALL 11 STAGES COMPLETED SUCCESSFULLY IN {total_duration:.1f}s ")
    print("=" * 72)


if __name__ == "__main__":
    main()
