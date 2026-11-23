"""
[Stage_02]_(Network_Graph_Construction_and_Centrality).py
---------------------------------------------------------
STAGE 2: Directed Weighted Network Graph Construction & Bottleneck Auditing.
- Constructs NetworkX directed weighted multigraph G = (V, E).
- 1,589 Hubs (Nodes) and 2,501 Directed Corridors (Edges).
- Edge weights = Median actual-vs-OSRM delay ratio stratified by route type and hour.
- Computes Betweenness Centrality, In/Out Degrees, and Chokepoint Risk Scores (0-100).
Outputs: data/logistics_graph.pkl, data/hub_centrality_metrics.csv, data/corridor_metrics.csv
"""

import os
import sys
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.graph_builder import run_graph_pipeline


def run_stage():
    print("=" * 75)
    print(" [STAGE 02] DIRECTED WEIGHTED NETWORK GRAPH & CHOKEPOINT AUDIT ")
    print("=" * 75)
    t0 = time.time()
    G, hubs_df, corr_df = run_graph_pipeline()
    print(f"\n>>> Stage 02 successfully completed in {time.time() - t0:.2f}s!")
    print(f">>> Graph Nodes: {G.number_of_nodes():,} hubs | Directed Edges: {G.number_of_edges():,} corridors")
    print(">>> Output Artifacts: data/logistics_graph.pkl, data/hub_centrality_metrics.csv, data/corridor_metrics.csv")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    run_stage()
