"""
src/run_pipeline.py
-------------------
End-to-End Master Pipeline Runner for Delhivery Logistics Network Intelligence.
Executes:
1. Data Preprocessing & Segment Aggregation
2. Graph Construction, Centrality & Bottleneck Auditing
3. Node2Vec & GraphSAGE Node Feature Generation
4. Machine Learning ETA Model Training & Benchmarking
5. FTL vs. Carting Decision Framework
6. Executive Operations Strategy Memo & ROI Quantification
"""

import sys
import time
from src.data_prep import prepare_and_save_data
from src.graph_builder import run_graph_pipeline
from src.node_embeddings import run_embedding_pipeline
from src.models import run_modeling_pipeline
from src.decision_framework import run_decision_framework
from src.strategy_memo import StrategyMemoGenerator


def main():
    print("=" * 70)
    print("  DELHIVERY NETWORK INTELLIGENCE: END-TO-END PIPELINE RUNNER  ")
    print("=" * 70)
    start_time = time.time()

    # Step 1: Preprocessing
    print("\n[STEP 1/6] Ingesting & Preprocessing Delhivery Shipment Segments...")
    prepare_and_save_data()

    # Step 2: Graph Construction & Centrality Audit
    print("\n[STEP 2/8] Building Directed Weighted Network Graph & Chokepoint Audit...")
    run_graph_pipeline()

    # Step 2b: Geocoding Hubs across India
    print("\n[STEP 2b/8] Geocoding Logistics Facilities Across India...")
    from src.geo_mapper import enrich_hubs_with_geocoordinates
    enrich_hubs_with_geocoordinates()

    # Step 3: Embeddings
    print("\n[STEP 3/8] Generating Node2Vec Embeddings & GraphSAGE Features...")
    run_embedding_pipeline()

    # Step 4: Machine Learning ETA Modeling & Benchmarking
    print("\n[STEP 4/8] Training & Benchmarking Baseline vs. Graph-Enhanced ETA Models...")
    run_modeling_pipeline()

    # Step 4b: Deep Graph Neural Network (GraphSAGE on PyG)
    print("\n[STEP 4b/8] Training Deep PyTorch Geometric GraphSAGE GNN...")
    from src.gnn_graphsage import run_gnn_pipeline
    run_gnn_pipeline()

    # Step 5: FTL vs Carting Decision Framework
    print("\n[STEP 5/8] Building FTL vs. Carting Route-Type Decision Framework...")
    run_decision_framework()

    # Step 6: Operations Strategy Memo & Impact Simulation
    print("\n[STEP 6/8] Generating Executive Strategy Memo & ROI Model...")
    gen = StrategyMemoGenerator()
    gen.run_and_save()

    # Step 7: Publication Visualizations & Presentation Slides
    print("\n[STEP 7/8] Generating High-Resolution Charts & PowerPoint Deck...")
    from src.visualize import generate_all_figures
    generate_all_figures()

    from generate_presentation import build_powerpoint_deck
    build_powerpoint_deck()

    # Step 8: Formal PDF Consulting Report
    print("\n[STEP 8/8] Generating Publication-Grade PDF Report...")
    from src.pdf_generator import generate_executive_pdf_report
    generate_executive_pdf_report()

    total_duration = time.time() - start_time
    print("\n" + "=" * 70)
    print(f" ALL PIPELINE MODULES COMPLETED SUCCESSFULLY IN {total_duration:.1f}s ")
    print("=" * 70)


if __name__ == "__main__":
    main()

