# LogiGraph AI: Stage-Wise Architecture & Execution Guide

This folder organizes the end-to-end Delhivery Logistics Network Intelligence system into **12 chronological stages**. Each stage is self-contained, fully documented, and can be executed independently.

---

## 📋 Summary of Pipeline Stages

| Stage File | Stage Name | Inputs | Primary Outputs | Academic & Algorithmic Significance |
| :--- | :--- | :--- | :--- | :--- |
| **`[Stage_01]_(Data_Ingestion_and_Preprocessing).py`** | Data Ingestion & Preprocessing | `delhivery_data.csv` (144k scans) | `cleaned_segments.csv` (26,214 legs) | Segment aggregation, outlier rejection, zero-leakage chronological split (72% train / 28% test). |
| **`[Stage_02]_(Network_Graph_Construction_and_Centrality).py`** | Network Graph & Centrality Audit | `cleaned_segments.csv` | `logistics_graph.pkl`, `hub_centrality_metrics.csv` | Directed weighted graph ($G=(V,E)$), 1,589 hubs, 2,501 corridors, Betweenness Centrality $C_B(v)$, Chokepoint Risk Scores. |
| **`[Stage_03]_(Geospatial_Mapping_and_Coordinates).py`** | Facility Geospatial Mapping | Hub names & center codes | `hubs_geocoded.csv` | Geocodes 1,589 Indian facilities with verified latitude/longitude coordinates for spatial map layers. |
| **`[Stage_04]_(Node2Vec_Embeddings_and_Neighborhood_Features).py`** | Representation Learning | `logistics_graph.pkl` | `node2vec_embeddings.pkl`, `graphsage_node_features.csv` | 16-dimensional Node2Vec random-walk embeddings ($p=1.0, q=0.5$) and 1-hop inductive neighborhood aggregations. |
| **`[Stage_05]_(Baseline_vs_Graph_ML_Benchmarking).py`** | ML Modeling & Benchmarking | Preprocessed features + embeddings | `best_graph_model.joblib`, `benchmark_results.json` | Benchmarks OSRM vs Baseline vs Graph-Enhanced Gradient Boosting; proves **28.13% error reduction** in MAE. |
| **`[Stage_06]_(Deep_GraphSAGE_GNN_PyTorch_Geometric).py`** | Deep GraphSAGE GNN | PyG graph tensors | `graphsage_gnn.pt` | 2-Layer inductive Graph Convolution Network (`SAGEConv`) in PyTorch Geometric achieving 36.0 min MAE. |
| **`[Stage_07]_(FTL_vs_Carting_Route_Type_Decision_Framework).py`** | Route Decision Framework | Segment costs & dwell times | `ftl_vs_carting_rules.csv` | Mathematical cost and time trade-off models; calculates breakeven distance $D^* = 21.875 \cdot h\text{ km}$. |
| **`[Stage_08]_(Operations_Strategy_Memo_and_ROI_Simulation).py`** | Strategic ROI Simulation | Centrality + Delay breaches | `operations_strategy_memo.md`, `strategy_impact_metrics.json` | Simulates modernizing top 3 hubs (Gurgaon, Bangalore, Bhiwandi) $\rightarrow$ **7.01% late shipment reduction**, recovering **₹3.24 Crores**. |
| **`[Stage_09]_(Dynamic_Congestion_Bypass_Router).py`** | Dynamic Bypass Routing Engine | Cost-weighted network graph | Rerouting metrics | Cost-weighted Dijkstra rerouting around severe bottlenecks, saving **5.3 hours** and **+₹2,080** net value. |
| **`[Stage_10]_(Publication_Figures_and_Visualizations).py`** | Publication Visualizations | Cleaned data & model results | `reports/figures/fig[1-5]*.png` | High-resolution publication-quality PNG charts. |
| **`[Stage_11]_(Executive_Master_PDF_Report_Builder).py`** | Master PDF Report Builder | Figures, benchmarks, memos | `Delhivery_Logistics_Optimization_Full_Project_Report.pdf` | ReportLab publication document (1.87 MB) with running canvas, tables, and viva Q&A. |
| **`[Stage_12]_(Master_Pipeline_Runner_All_Stages).py`** | Master Pipeline Orchestrator | All modules | End-to-end execution | Runs all stages in sequence from raw data ingestion to master PDF report export. |

---

## 🚀 How to Execute Any Stage

You can run any individual stage from the project root:

```bash
# Example 1: Run Stage 01 (Data Preprocessing)
python "stages/[Stage_01]_(Data_Ingestion_and_Preprocessing).py"

# Example 2: Run Stage 05 (ML Modeling & The Graph Advantage)
python "stages/[Stage_05]_(Baseline_vs_Graph_ML_Benchmarking).py"

# Example 3: Run Stage 09 (Dynamic Congestion Bypass Router)
python "stages/[Stage_09]_(Dynamic_Congestion_Bypass_Router).py"

# Example 4: Run All Stages Sequentially
python "stages/[Stage_12]_(Master_Pipeline_Runner_All_Stages).py"
```
