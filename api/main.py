"""
api/main.py
-----------
Production REST API for Delhivery Logistics Network Intelligence (powered by Flask & Werkzeug).
Provides real-time ETA inference, chokepoint auditing, route-type recommendations,
and dynamic bypass optimization for external TMS (Transportation Management Systems).
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import joblib

app = Flask(__name__)
CORS(app)

# Global runtime cache
MODELS = {}
DATA = {}


def load_artifacts():
    print("Loading API runtime artifacts...")
    try:
        MODELS['best_graph_model'] = joblib.load("models/best_graph_model.joblib")
        MODELS['baseline_model'] = joblib.load("models/baseline_model.joblib")
        with open("models/benchmark_results.json", "r") as f:
            MODELS['benchmarks'] = json.load(f)
        with open("data/logistics_graph.pkl", "rb") as f:
            DATA['graph_data'] = pickle.load(f)
        with open("data/node2vec_embeddings.pkl", "rb") as f:
            DATA['node2vec_data'] = pickle.load(f)

        DATA['hubs_df'] = pd.read_csv("data/hubs_geocoded.csv" if os.path.exists("data/hubs_geocoded.csv") else "data/hub_centrality_metrics.csv")
        DATA['corridors_df'] = pd.read_csv("data/corridor_metrics.csv")
        DATA['rules_df'] = pd.read_csv("data/ftl_vs_carting_rules.csv")
        print("API runtime artifacts initialized successfully.")
    except Exception as e:
        print(f"Warning loading artifacts: {e}")


# Initialize artifacts at module load
load_artifacts()


@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "service": "Delhivery Logistics Network Intelligence API",
        "version": "2.0.0",
        "status": "online",
        "framework": "Flask 3.1",
        "endpoints": [
            "/api/v1/health",
            "/api/v1/hubs",
            "/api/v1/corridors/bottlenecks",
            "/api/v1/predict/eta",
            "/api/v1/recommend/route-type",
            "/api/v1/route/optimize"
        ]
    })


@app.route("/api/v1/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "models_loaded": list(MODELS.keys()),
        "hub_count": len(DATA.get('hubs_df', [])),
        "corridor_count": len(DATA.get('corridors_df', []))
    })


@app.route("/api/v1/hubs", methods=["GET"])
def get_hubs():
    limit = int(request.args.get("limit", 50))
    sort_by_risk = request.args.get("sort_by_risk", "true").lower() == "true"

    if 'hubs_df' not in DATA:
        return jsonify({"error": "Hub data not loaded"}), 503

    df = DATA['hubs_df']
    if sort_by_risk and 'chokepoint_risk_score' in df.columns:
        df = df.sort_values('chokepoint_risk_score', ascending=False)
    return jsonify(df.head(limit).to_dict(orient="records"))


@app.route("/api/v1/corridors/bottlenecks", methods=["GET"])
def get_delayed_corridors():
    min_delay = float(request.args.get("min_delay_ratio", 1.5))
    limit = int(request.args.get("limit", 50))

    if 'corridors_df' not in DATA:
        return jsonify({"error": "Corridor data not loaded"}), 503

    df = DATA['corridors_df']
    filtered = df[df['median_delay_ratio'] >= min_delay].sort_values('median_delay_ratio', ascending=False)
    return jsonify(filtered.head(limit).to_dict(orient="records"))


@app.route("/api/v1/predict/eta", methods=["POST"])
def predict_eta():
    req = request.get_json(force=True)
    src_id = req.get("source_hub_id")
    dst_id = req.get("destination_hub_id")
    dist_km = float(req.get("distance_km", 250.0))
    rtype = req.get("route_type", "FTL")
    hour = int(req.get("departure_hour", 14))
    dow = int(req.get("day_of_week", 2))

    if 6 <= hour < 12:
        tod = "Morning"
    elif 12 <= hour < 18:
        tod = "Afternoon"
    elif 18 <= hour < 24:
        tod = "Evening"
    else:
        tod = "Night"

    is_weekend = 1 if dow in [5, 6] else 0
    is_ftl = 1 if rtype.upper() == 'FTL' else 0
    osrm_time_hr = round(dist_km / 50.0, 2)

    b_feat = [
        osrm_time_hr, dist_km, is_ftl, hour, dow, is_weekend,
        1 if tod == 'Morning' else 0, 1 if tod == 'Afternoon' else 0, 1 if tod == 'Evening' else 0, 1 if tod == 'Night' else 0,
        1 if dist_km < 100 else 0, 1 if 100 <= dist_km <= 300 else 0, 1 if dist_km > 300 else 0
    ]

    graph_data = DATA['graph_data']
    strat_dict = graph_data['stratified_corridor_dict']
    global_median = graph_data['global_median_delay_ratio']
    embeddings = DATA['node2vec_data']['embeddings']
    emb_dim = DATA['node2vec_data']['dimensions']

    corr_key = (src_id, dst_id, rtype, tod)
    corr_weight = strat_dict.get(corr_key, global_median)
    corr_chronic = 1 if corr_weight > 1.20 else 0

    hubs_df = DATA['hubs_df']
    src_m = hubs_df[hubs_df['hub_id'] == src_id]
    dst_m = hubs_df[hubs_df['hub_id'] == dst_id]

    src_bc = float(src_m['betweenness_centrality'].values[0]) if not src_m.empty else 0.0
    dst_bc = float(dst_m['betweenness_centrality'].values[0]) if not dst_m.empty else 0.0
    src_choke = float(src_m['chokepoint_risk_score'].values[0]) if not src_m.empty else 15.0
    dst_choke = float(dst_m['chokepoint_risk_score'].values[0]) if not dst_m.empty else 15.0

    src_emb = embeddings.get(str(src_id), np.zeros(emb_dim, dtype=np.float32))
    dst_emb = embeddings.get(str(dst_id), np.zeros(emb_dim, dtype=np.float32))
    norm_src = np.linalg.norm(src_emb)
    norm_dst = np.linalg.norm(dst_emb)
    cosine_sim = float(np.dot(src_emb, dst_emb) / (norm_src * norm_dst + 1e-9))
    euclid_dist = float(np.linalg.norm(src_emb - dst_emb))

    g_feat = b_feat + [
        corr_weight, corr_chronic,
        src_bc, dst_bc,
        float(src_m['in_degree'].values[0]) if not src_m.empty else 0.0,
        float(src_m['out_degree'].values[0]) if not src_m.empty else 0.0,
        float(dst_m['in_degree'].values[0]) if not dst_m.empty else 0.0,
        float(dst_m['out_degree'].values[0]) if not dst_m.empty else 0.0,
        float(src_m['clustering_coefficient'].values[0]) if not src_m.empty else 0.0,
        float(dst_m['clustering_coefficient'].values[0]) if not dst_m.empty else 0.0,
        src_choke, dst_choke,
        float(src_m['hub_sla_breach_rate'].values[0]) if not src_m.empty else 0.88,
        float(dst_m['hub_sla_breach_rate'].values[0]) if not dst_m.empty else 0.88,
        1.88, 1.88, 15.0, 15.0,
        cosine_sim, euclid_dist
    ] + src_emb.tolist() + dst_emb.tolist()

    pred_baseline = float(MODELS['baseline_model'].predict([b_feat])[0])
    pred_graph = float(MODELS['best_graph_model'].predict([g_feat])[0])

    delay_gap_pct = round(((pred_graph - osrm_time_hr) / osrm_time_hr) * 100, 1)
    if delay_gap_pct > 50 or src_choke > 60:
        risk_level = "High Risk"
    elif delay_gap_pct > 20:
        risk_level = "Moderate Risk"
    else:
        risk_level = "Normal"

    return jsonify({
        "source_hub_id": src_id,
        "destination_hub_id": dst_id,
        "distance_km": dist_km,
        "osrm_baseline_eta_hours": osrm_time_hr,
        "trip_level_ml_eta_hours": round(pred_baseline, 2),
        "graph_enhanced_eta_hours": round(pred_graph, 2),
        "graph_enhanced_eta_minutes": round(pred_graph * 60, 1),
        "expected_delay_vs_osrm_percent": delay_gap_pct,
        "delay_risk_category": risk_level,
        "source_chokepoint_risk_score": round(src_choke, 1),
        "corridor_historical_delay_ratio": round(corr_weight, 2)
    })


@app.route("/api/v1/recommend/route-type", methods=["POST"])
def recommend_route_type():
    req = request.get_json(force=True)
    src_id = req.get("source_hub_id")
    dist_km = float(req.get("distance_km", 200.0))
    is_time_critical = bool(req.get("is_time_critical", False))

    hubs_df = DATA.get('hubs_df')
    hub_match = hubs_df[hubs_df['hub_id'] == src_id] if hubs_df is not None else pd.DataFrame()
    choke_val = float(hub_match.iloc[0]['chokepoint_risk_score']) if not hub_match.empty else 20.0

    cost_ftl = (dist_km * 38.0) + (0.82 * 1200.0)
    cost_carting = (dist_km * 22.0 + 350.0) + (0.91 * 1200.0)

    if is_time_critical or choke_val > 60.0 or dist_km > 300:
        rec_mode = "FTL (Dedicated)"
        reason = f"Shipment originates at high-chokepoint hub ({choke_val:.1f}) or long haul ({dist_km:.1f} km). FTL eliminates intermediate sorting dwell."
    else:
        rec_mode = "Carting (Consolidated)"
        saving = max(0, cost_ftl - cost_carting)
        reason = f"Short/medium haul from low-risk facility. Carting saves an estimated INR {saving:.0f} per shipment."

    return jsonify({
        "source_hub_id": src_id,
        "distance_km": dist_km,
        "recommended_mode": rec_mode,
        "estimated_ftl_cost_inr": round(cost_ftl, 0),
        "estimated_carting_cost_inr": round(cost_carting, 0),
        "operational_rationale": reason
    })


@app.route("/api/v1/route/optimize", methods=["POST"])
def optimize_route():
    req = request.get_json(force=True)
    orig = req.get("origin_hub_id")
    dest = req.get("destination_hub_id")

    from src.route_optimizer import DynamicRouteOptimizer
    opt = DynamicRouteOptimizer()
    opt.load_network()
    result = opt.find_routes(orig, dest)
    return jsonify(result)


@app.route("/download/report", methods=["GET"])
def download_pdf_report():
    pdf_path = os.path.abspath("reports/Delhivery_Logistics_Optimization_Full_Project_Report.pdf")
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True, download_name="Delhivery_Logistics_Optimization_Full_Project_Report.pdf", mimetype='application/pdf')
    return jsonify({"error": "Report PDF not found"}), 404


@app.route("/download/presentation", methods=["GET"])
def download_presentation():
    pptx_path = os.path.abspath("presentation_slides.pptx")
    if os.path.exists(pptx_path):
        return send_file(pptx_path, as_attachment=True, download_name="Delhivery_Logistics_Optimization_Presentation.pptx", mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation')
    return jsonify({"error": "Presentation PPTX not found"}), 404


@app.route("/view/report", methods=["GET"])
def view_pdf_report():
    pdf_path = os.path.abspath("reports/Delhivery_Logistics_Optimization_Full_Project_Report.pdf")
    if os.path.exists(pdf_path):
        return send_file(pdf_path, mimetype='application/pdf')
    return jsonify({"error": "Report PDF not found"}), 404


if __name__ == "__main__":
    print("Starting Flask API server on port 8000...")
    app.run(host="0.0.0.0", port=8000, debug=False)
