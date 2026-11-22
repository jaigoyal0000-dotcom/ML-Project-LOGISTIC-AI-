"""
tests/test_pipeline.py
----------------------
Automated test suite verifying data pipelines, graph construction,
models, predictions, decision frameworks, geocoding, route optimization, and APIs.
"""

import os
import sys
import json
import pickle
import numpy as np
import pandas as pd
import joblib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_artifacts_exist():
    required_files = [
        "data/cleaned_segments.csv",
        "data/hub_centrality_metrics.csv",
        "data/hubs_geocoded.csv",
        "data/corridor_metrics.csv",
        "data/logistics_graph.pkl",
        "data/node2vec_embeddings.pkl",
        "data/graphsage_node_features.csv",
        "data/ftl_vs_carting_rules.csv",
        "models/best_graph_model.joblib",
        "models/baseline_model.joblib",
        "models/benchmark_results.json",
        "models/feature_importance.csv",
        "reports/operations_strategy_memo.md",
        "reports/Delhivery_Network_Optimization_Report.pdf",
        "reports/strategy_impact_metrics.json",
        "reports/figures/fig1_osrm_delay_distribution.png",
        "reports/figures/fig2_top_chokepoints_sla_breaches.png",
        "reports/figures/fig3_network_topology_bottlenecks.png",
        "reports/figures/fig4_graph_advantage_benchmarks.png",
        "reports/figures/fig5_ftl_vs_carting_tradeoff.png",
        "presentation_slides.pptx"
    ]
    for f in required_files:
        assert os.path.exists(f), f"Missing required file: {f}"
    print("[PASS] All required system artifacts and figures exist.")


def test_data_integrity():
    df = pd.read_csv("data/cleaned_segments.csv")
    assert len(df) > 20000, f"Expected >20k segments, got {len(df)}"
    assert 'delay_ratio' in df.columns
    assert 'sla_breached' in df.columns
    assert df['delay_ratio'].min() >= 0.1
    assert df['delay_ratio'].max() <= 15.0
    print(f"[PASS] Data integrity verified: {len(df):,} cleaned segments loaded successfully.")


def test_graph_and_hubs():
    hubs = pd.read_csv("data/hubs_geocoded.csv")
    assert len(hubs) > 1000, f"Expected >1000 hubs, got {len(hubs)}"
    assert 'betweenness_centrality' in hubs.columns
    assert 'chokepoint_risk_score' in hubs.columns
    assert 'latitude' in hubs.columns and 'longitude' in hubs.columns

    top_hub = hubs.iloc[0]
    assert "IND000000ACB" in top_hub['hub_id'] or "Gurgaon" in str(top_hub['hub_name'])
    print(f"[PASS] Hub graph & geospatial coordinates verified: Top Chokepoint is {top_hub['hub_name']} (Score: {top_hub['chokepoint_risk_score']:.1f}).")


def test_model_inference():
    best_model = joblib.load("models/best_graph_model.joblib")
    with open("models/benchmark_results.json", "r") as f:
        benchmarks = json.load(f)

    gb_row = next(b for b in benchmarks if "Graph-Enhanced: Gradient Boosting" in b['Model'])
    base_row = next(b for b in benchmarks if "Baseline: Gradient Boosting" in b['Model'])

    assert gb_row['MAE (Hours)'] < base_row['MAE (Hours)'], "Graph model must outperform baseline on MAE"
    assert gb_row['Within-15% Accuracy (%)'] > base_row['Within-15% Accuracy (%)'], "Graph model must outperform baseline on 15% accuracy"

    dummy_input = np.ones((1, 65), dtype=np.float32)
    pred = best_model.predict(dummy_input)
    assert pred.shape == (1,)
    assert pred[0] > 0.0
    print(f"[PASS] Model inference verified: Dummy prediction = {pred[0]:.2f} hrs. Graph Advantage confirmed.")


def test_decision_framework():
    from src.decision_framework import RouteTypeDecisionEngine
    engine = RouteTypeDecisionEngine()
    engine.load_and_merge()

    rec_short = engine.recommend(distance_km=45.0, source_hub_id="IND562101AAA", is_time_critical=False)
    assert rec_short['recommended_route_type'] in ['Carting', 'FTL']

    rec_long = engine.recommend(distance_km=850.0, source_hub_id="IND000000ACB", is_time_critical=True)
    assert rec_long['recommended_route_type'] == 'FTL'
    print("[PASS] FTL vs. Carting decision framework operational logic verified.")


def test_route_optimizer():
    from src.route_optimizer import DynamicRouteOptimizer
    opt = DynamicRouteOptimizer()
    opt.load_network()
    res = opt.find_routes("IND000000ACB", "IND562132AAA")
    assert 'standard_route' in res
    assert 'dynamic_bypass_route' in res
    assert res['standard_route']['expected_transit_hr'] > 0.0
    print(f"[PASS] Dynamic Route Optimizer verified: Route calculated with recommendation '{res['recommendation']}'.")


def test_api_endpoints():
    from api.main import app
    client = app.test_client()
    resp = client.get('/api/v1/health')
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'healthy'
    print("[PASS] REST API endpoints verified.")


if __name__ == "__main__":
    print("\n=== RUNNING ADVANCED LOGIGRAPH AI TEST SUITE ===")
    test_artifacts_exist()
    test_data_integrity()
    test_graph_and_hubs()
    test_model_inference()
    test_decision_framework()
    test_route_optimizer()
    test_api_endpoints()
    print("\n>>> ALL 7 TEST MODULES PASSED WITH 100% SUCCESS! <<<\n")
