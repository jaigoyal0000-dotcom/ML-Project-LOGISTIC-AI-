# Optimizing Delivery ETAs with Graph-Based Network Intelligence
### LogiGraph AI · Delhivery Logistics Network

An end-to-end Machine Learning and Graph Intelligence system that predicts delivery transit times (ETAs), audits national logistics bottlenecks, and provides automated decision frameworks for route types (FTL vs. Carting) and capital facility upgrades.

---

## 🌟 Key Results & "The Graph Advantage"

| Model Architecture | MAE (Hours) | MAE (Minutes) | Within-15% Accuracy (%) | Within-25% Accuracy (%) | R² Score |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **OSRM Routing Engine (Reference)** | 1.489 h | 89.3 min | 7.06% | 13.80% | 0.726 |
| **Baseline: Linear Regression** | 0.766 h | 46.0 min | 27.90% | 42.92% | 0.935 |
| **Baseline: Gradient Boosting (Trip-Level)** | 0.711 h | 42.7 min | 30.27% | 46.98% | 0.944 |
| **Graph-Enhanced: Deep GraphSAGE GNN (PyG)** | **0.600 h** | **36.0 min** | **43.74%** | **63.45%** | **0.944** |
| **Graph-Enhanced: Gradient Boosting (Best Model)** | **0.511 h** | **30.7 min** | **48.67%** | **67.45%** | **0.961** |

> **The Graph Advantage:** **28.13% error reduction in MAE** and **+18.40 percentage points gain in Within-15% prediction accuracy**.

---

## 🏗️ Project Architecture

```
ml_proj/
├── data/
│   ├── delhivery_data.csv            # Original historical shipment data (144k+ records)
│   ├── cleaned_segments.csv          # Preprocessed corridor hops (26k+ segments)
│   ├── hub_centrality_metrics.csv    # Centrality, degrees & chokepoint risk scores
│   ├── hubs_geocoded.csv             # Indian facilities with latitude and longitude
│   ├── corridor_metrics.csv          # Corridor median delay ratios & chronic delay flags
│   ├── node2vec_embeddings.pkl       # 16-dimensional Node2Vec hub embeddings
│   ├── graphsage_node_features.csv   # GraphSAGE 1-hop neighborhood aggregations
│   ├── ftl_vs_carting_rules.csv      # Empirical FTL vs Carting trade-off matrix
│   └── logistics_graph.pkl           # Serialized NetworkX directed weighted graph
├── src/
│   ├── data_prep.py                  # Step 1: Cleaning, aggregation, and leakage prevention
│   ├── graph_builder.py              # Step 2: Directed weighted graph & bottleneck audit
│   ├── geo_mapper.py                 # Step 2b: Indian geocoding for spatial map layers
│   ├── node_embeddings.py            # Step 3: Node2Vec & GraphSAGE feature generation
│   ├── models.py                     # Step 4: Baseline vs Graph-Enhanced ML benchmarking
│   ├── gnn_graphsage.py              # Step 4b: Deep GraphSAGE GNN on PyTorch Geometric
│   ├── decision_framework.py         # Step 5: FTL vs Carting time-cost-SLA engine
│   ├── strategy_memo.py              # Step 6: Operations leadership strategy memo & ROI
│   ├── visualize.py                  # Step 7: Publication-quality charts generator
│   ├── pdf_generator.py              # Step 8: Executive PDF Consulting Report builder
│   ├── route_optimizer.py            # Dynamic chokepoint-bypass routing engine
│   └── run_pipeline.py               # Master end-to-end execution runner
├── api/
│   └── main.py                       # Production REST API (Flask & Werkzeug)
├── app/
│   └── app.py                        # Advanced Streamlit Interactive Web Application (8 views)
├── models/
│   ├── best_graph_model.joblib       # Production Graph-Enhanced Gradient Boosting model
│   ├── baseline_model.joblib         # Baseline trip-level regression model
│   ├── graphsage_gnn.pt              # Trained PyTorch Geometric GraphSAGE checkpoint
│   ├── benchmark_results.json        # Comparative benchmark evaluation metrics
│   ├── feature_importance.csv        # Top predictive features ranking
│   └── pipeline_meta.json            # Graph advantage summary metadata
├── reports/
│   ├── operations_strategy_memo.md   # Executive Strategy Memo for VP of Logistics
│   ├── Delhivery_Network_Optimization_Report.pdf # Publication-grade Consulting PDF Report
│   ├── presentation_guide.md         # Faculty Presentation Script & 16 Viva Q&As
│   ├── strategy_impact_metrics.json  # Hub upgrade ROI simulation metrics
│   └── figures/                      # 5 high-res PNG charts for presentations
├── tests/
│   └── test_pipeline.py              # Automated 7-module test suite (100% pass)
├── presentation_slides.pptx          # 10-slide ready-to-present PowerPoint deck
├── run_dashboard.bat                 # One-click desktop launcher for web dashboard
├── run_api.bat                       # One-click desktop launcher for REST API
├── run_pipeline.bat                  # One-click pipeline runner
└── requirements.txt
```

---

## 🚀 Quickstart Guide

### 1. Run Complete Pipeline End-to-End
To regenerate datasets, build the network graph, train all ML models, and generate the strategy memo:
```powershell
python -m src.run_pipeline
```

### 2. Launch Interactive Streamlit Dashboard
```powershell
streamlit run app/app.py
```
Open your browser at `http://localhost:8501` to access:
1. **Executive Overview & KPIs:** Delay distribution curves and state-level breach concentrations.
2. **Network Topology & Corridors:** Interactive corridor inspector and delay filter.
3. **Hub Bottleneck & Chokepoints:** Top 10 Chokepoint Leaderboard and facility inspector.
4. **Live Smart ETA Predictor:** Compare OSRM vs. Baseline vs. Graph Model predictions with delay risk alerts.
5. **FTL vs. Carting Decision Framework:** Interactive trade-off simulator.
6. **Strategy Memo & Capital Upgrade ROI:** Real-time hub modernization simulator.
7. **Model Benchmarking:** Visual comparison of MAE and Within-15% accuracy.

---

## 🏆 Top 5 National Chokepoint Hubs

1. **Gurgaon Bilaspur (`IND000000ACB`, Haryana)**: Betweenness Centrality: 0.214 | 1,225 SLA Breaches | Chokepoint Score: 97.7/100
2. **Bangalore Nelamangala (`IND562132AAA`, Karnataka)**: Betweenness Centrality: 0.114 | 962 SLA Breaches | Chokepoint Score: 69.2/100
3. **Bhiwandi Mankoli (`IND421302AAG`, Maharashtra)**: 965 SLA Breaches | Chokepoint Score: 59.4/100
4. **Hyderabad Shamshabad (`IND501359AAE`, Telangana)**: Betweenness Centrality: 0.083 | 530 SLA Breaches | Chokepoint Score: 46.8/100
5. **Kolkata Dankuni (`IND712311AAA`, West Bengal)**: Betweenness Centrality: 0.095 | 367 SLA Breaches | Chokepoint Score: 44.5/100

Modernizing the top 3 hubs prevents **{prevented} late deliveries**, achieving a **7.01% network-wide reduction in SLA failures** and recovering **₹3.24 Crores in annualized revenue-at-risk**.

