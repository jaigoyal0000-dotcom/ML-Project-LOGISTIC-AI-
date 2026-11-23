"""
[Stage_04]_(Node2Vec_Embeddings_and_Neighborhood_Features).py
--------------------------------------------------------------
STAGE 4: Representation Learning via Biased Random Walks & GraphSAGE Features.
- Simulates biased second-order random walks (p=1.0, q=0.5, walk_length=10).
- Generates continuous 16-dimensional vector representations for each logistics hub.
- Extracts 1-hop GraphSAGE inductive neighborhood delay and connectivity features.
Outputs: data/node2vec_embeddings.pkl, data/graphsage_node_features.csv
"""

import os
import sys
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.node_embeddings import run_embedding_pipeline


def run_stage():
    print("=" * 75)
    print(" [STAGE 04] NODE2VEC EMBEDDINGS & GRAPHSAGE NEIGHBORHOOD FEATURES ")
    print("=" * 75)
    t0 = time.time()
    n2v, gs_df = run_embedding_pipeline()
    print(f"\n>>> Stage 04 successfully completed in {time.time() - t0:.2f}s!")
    print(f">>> Generated 16-D embeddings for {len(n2v.get('embeddings', {})):,} hubs.")
    print(">>> Output Artifacts: data/node2vec_embeddings.pkl, data/graphsage_node_features.csv")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    run_stage()
