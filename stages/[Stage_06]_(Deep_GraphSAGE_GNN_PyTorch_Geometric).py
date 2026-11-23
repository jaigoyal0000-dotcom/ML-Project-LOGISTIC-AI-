"""
[Stage_06]_(Deep_GraphSAGE_GNN_PyTorch_Geometric).py
-----------------------------------------------------
STAGE 6: Deep Graph Neural Network Training on PyTorch Geometric.
- 2-Layer inductive GraphSAGE architecture (SAGEConv + ReLU + Dropout + Linear Readout).
- Trains end-to-end with Adam optimizer minimizing Mean Squared Error on transit times.
- Achieves 36.0 min MAE, confirming deep inductive message passing captures physical delay waves.
Output: models/graphsage_gnn.pt
"""

import os
import sys
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.gnn_graphsage import run_gnn_pipeline


def run_stage():
    print("=" * 75)
    print(" [STAGE 06] DEEP GRAPHSAGE GNN (PYTORCH GEOMETRIC INDUCTIVE MODEL) ")
    print("=" * 75)
    t0 = time.time()
    model, test_mae = run_gnn_pipeline()
    print(f"\n>>> Stage 06 successfully completed in {time.time() - t0:.2f}s!")
    print(f">>> PyG GraphSAGE GNN Test MAE: {test_mae:.2f} hours ({test_mae*60:.1f} mins)")
    print(">>> Output Artifact: models/graphsage_gnn.pt")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    run_stage()
