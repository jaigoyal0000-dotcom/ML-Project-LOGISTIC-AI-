"""
src/gnn_graphsage.py
--------------------
Deep Graph Neural Network (GraphSAGE) using PyTorch Geometric (PyG).
Learns inductive representations of logistics hubs via SAGEConv neighborhood aggregation
and trains an end-to-end multi-layer perceptron for trip-level ETA regression.
"""

import os
import json
import time
import pickle
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def compute_within_pct_accuracy(y_true, y_pred, pct=0.15):
    y_true = np.asarray(y_true, dtype=np.float64)
    y_pred = np.asarray(y_pred, dtype=np.float64)
    denom = np.where(y_true == 0, 1e-6, y_true)
    rel_error = np.abs(y_pred - y_true) / np.abs(denom)
    return float(np.mean(rel_error <= pct) * 100.0)


class GraphSAGENetwork(nn.Module):
    """
    2-Layer GraphSAGE node encoder combined with a dual-hub link prediction MLP.
    """
    def __init__(self, in_channels=6, hidden_dim=32, emb_dim=16, trip_feat_dim=6):
        super(GraphSAGENetwork, self).__init__()
        # Node convolution layers
        self.conv1 = SAGEConv(in_channels, hidden_dim, aggr='mean')
        self.conv2 = SAGEConv(hidden_dim, emb_dim, aggr='mean')

        # Link/Trip regression MLP: inputs = [src_emb (16) + dst_emb (16) + trip_features (6)] = 38
        combined_dim = emb_dim * 2 + trip_feat_dim
        self.mlp = nn.Sequential(
            nn.Linear(combined_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.15),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )

    def encode_nodes(self, x, edge_index):
        h = self.conv1(x, edge_index)
        h = F.relu(h)
        h = F.dropout(h, p=0.1, training=self.training)
        h = self.conv2(h, edge_index)
        return h

    def forward(self, x, edge_index, src_indices, dst_indices, trip_features):
        # 1. Compute node representations
        node_embeddings = self.encode_nodes(x, edge_index)

        # 2. Extract embeddings for specific source and destination pairs
        src_h = node_embeddings[src_indices]
        dst_h = node_embeddings[dst_indices]

        # 3. Concatenate and pass to ETA prediction MLP
        combined = torch.cat([src_h, dst_h, trip_features], dim=-1)
        out = self.mlp(combined)
        return out.squeeze(-1)


class GraphSAGETrainer:
    def __init__(self, data_path="data/cleaned_segments.csv", hub_path="data/hub_centrality_metrics.csv"):
        self.data_path = data_path
        self.hub_path = hub_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")

        self.df = None
        self.hubs_df = None
        self.hub_to_idx = {}
        self.num_nodes = 0
        self.node_features = None
        self.edge_index = None

    def prepare_graph_data(self):
        print("Preparing PyTorch Geometric graph tensors...")
        self.df = pd.read_csv(self.data_path)
        self.hubs_df = pd.read_csv(self.hub_path)

        # Map all hubs to contiguous indices
        all_hubs = sorted(self.hubs_df['hub_id'].unique().tolist())
        self.hub_to_idx = {h: i for i, h in enumerate(all_hubs)}
        self.num_nodes = len(all_hubs)

        # Node feature matrix: [in_degree, out_degree, betweenness, clustering, breach_rate, avg_out_delay]
        feat_cols = [
            'in_degree', 'out_degree', 'betweenness_centrality',
            'clustering_coefficient', 'hub_sla_breach_rate', 'avg_outbound_delay_ratio'
        ]
        hubs_indexed = self.hubs_df.set_index('hub_id').reindex(all_hubs).fillna(0.0)
        X_nodes = hubs_indexed[feat_cols].values.astype(np.float32)

        # Normalize features
        mean = np.mean(X_nodes, axis=0)
        std = np.std(X_nodes, axis=0) + 1e-6
        X_nodes = (X_nodes - mean) / std
        self.node_features = torch.tensor(X_nodes, dtype=torch.float, device=self.device)

        # Build edge index strictly from training trips to prevent leakage
        train_df = self.df[self.df['data'] == 'training']
        edges = train_df[['source_center', 'destination_center']].drop_duplicates()
        edge_src = [self.hub_to_idx[s] for s in edges['source_center'] if s in self.hub_to_idx and edges.loc[edges['source_center'] == s, 'destination_center'].iloc[0] in self.hub_to_idx]
        edge_dst = [self.hub_to_idx[d] for s, d in zip(edges['source_center'], edges['destination_center']) if s in self.hub_to_idx and d in self.hub_to_idx]

        self.edge_index = torch.tensor([edge_src, edge_dst], dtype=torch.long, device=self.device)
        print(f"Graph initialized: {self.num_nodes:,} nodes, {self.edge_index.size(1):,} directed training edges.")

    def prepare_trip_dataset(self, split='training'):
        split_df = self.df[self.df['data'] == split].copy()
        # Filter rows where both hubs are in hub_to_idx
        valid_mask = split_df['source_center'].isin(self.hub_to_idx) & split_df['destination_center'].isin(self.hub_to_idx)
        split_df = split_df[valid_mask].reset_index(drop=True)

        src_indices = [self.hub_to_idx[s] for s in split_df['source_center']]
        dst_indices = [self.hub_to_idx[d] for d in split_df['destination_center']]

        # Trip features: [osrm_time_hr, osrm_distance_km, is_ftl, start_hour, start_dayofweek, is_weekend]
        trip_feats = []
        for _, r in split_df.iterrows():
            osrm_t = float(r['osrm_time_hr'])
            osrm_d = float(r['osrm_distance_km'])
            is_ftl = 1.0 if r['route_type'] == 'FTL' else 0.0
            hr = float(r['start_hour']) / 24.0 # normalize
            dow = float(r['start_dayofweek']) / 7.0
            is_wk = 1.0 if r['start_dayofweek'] in [5, 6] else 0.0
            trip_feats.append([osrm_t, osrm_d / 500.0, is_ftl, hr, dow, is_wk])

        y = split_df['actual_time_hr'].values.astype(np.float32)

        data_dict = {
            'src_indices': torch.tensor(src_indices, dtype=torch.long, device=self.device),
            'dst_indices': torch.tensor(dst_indices, dtype=torch.long, device=self.device),
            'trip_features': torch.tensor(trip_feats, dtype=torch.float, device=self.device),
            'y': torch.tensor(y, dtype=torch.float, device=self.device),
            'y_numpy': y
        }
        return data_dict

    def train_and_evaluate(self, epochs=25, lr=0.005, batch_size=512):
        print(f"\n--- Training Deep GraphSAGE Neural Network (Epochs={epochs}, LR={lr}) ---")
        train_data = self.prepare_trip_dataset('training')
        test_data = self.prepare_trip_dataset('test')

        model = GraphSAGENetwork(in_channels=6, hidden_dim=32, emb_dim=16, trip_feat_dim=6).to(self.device)
        optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
        criterion = nn.SmoothL1Loss()

        num_train = len(train_data['y'])
        indices = np.arange(num_train)

        start_time = time.time()
        for epoch in range(1, epochs + 1):
            model.train()
            np.random.shuffle(indices)
            total_loss = 0.0
            num_batches = 0

            for i in range(0, num_train, batch_size):
                b_idx = indices[i:i + batch_size]
                b_src = train_data['src_indices'][b_idx]
                b_dst = train_data['dst_indices'][b_idx]
                b_trips = train_data['trip_features'][b_idx]
                b_y = train_data['y'][b_idx]

                optimizer.zero_grad()
                pred = model(self.node_features, self.edge_index, b_src, b_dst, b_trips)
                loss = criterion(pred, b_y)
                loss.backward()
                optimizer.step()

                total_loss += loss.item()
                num_batches += 1

            if epoch % 5 == 0 or epoch == epochs:
                avg_loss = total_loss / max(1, num_batches)
                print(f"Epoch {epoch:02d}/{epochs:02d} | Train SmoothL1 Loss: {avg_loss:.4f}")

        train_duration = time.time() - start_time
        print(f"GraphSAGE training completed in {train_duration:.2f}s.")

        # Evaluation on Test Split
        model.eval()
        with torch.no_grad():
            test_preds = model(
                self.node_features,
                self.edge_index,
                test_data['src_indices'],
                test_data['dst_indices'],
                test_data['trip_features']
            ).cpu().numpy()

        test_preds = np.maximum(test_preds, 0.05)
        y_test = test_data['y_numpy']

        mae = float(mean_absolute_error(y_test, test_preds))
        rmse = float(np.sqrt(mean_squared_error(y_test, test_preds)))
        r2 = float(r2_score(y_test, test_preds))
        acc15 = compute_within_pct_accuracy(y_test, test_preds, pct=0.15)
        acc25 = compute_within_pct_accuracy(y_test, test_preds, pct=0.25)

        print("\n=== GRAPHSAGE GNN EVALUATION RESULTS ===")
        print(f" • MAE: {mae:.3f} hours ({mae * 60:.1f} mins)")
        print(f" • Within-15% Accuracy: {acc15:.2f}%")
        print(f" • Within-25% Accuracy: {acc25:.2f}%")
        print(f" • RMSE: {rmse:.3f} hours")
        print(f" • R² Score: {r2:.3f}")

        # Save model
        os.makedirs("models", exist_ok=True)
        torch.save({
            'state_dict': model.state_dict(),
            'hub_to_idx': self.hub_to_idx,
            'mae': mae,
            'acc15': acc15
        }, "models/graphsage_gnn.pt")

        sage_results = {
            'Model': 'Graph-Enhanced: Deep GraphSAGE GNN (PyTorch Geometric)',
            'MAE (Hours)': round(mae, 3),
            'MAE (Minutes)': round(mae * 60, 1),
            'Within-15% Accuracy (%)': round(acc15, 2),
            'Within-25% Accuracy (%)': round(acc25, 2),
            'RMSE (Hours)': round(rmse, 3),
            'R² Score': round(r2, 3),
            'Training Time (s)': round(train_duration, 2)
        }

        # Update benchmark JSON
        bench_path = "models/benchmark_results.json"
        if os.path.exists(bench_path):
            with open(bench_path, "r") as f:
                b_list = json.load(f)
            # Remove existing GraphSAGE if present, then append
            b_list = [b for b in b_list if "Deep GraphSAGE" not in b['Model']]
            b_list.append(sage_results)
            with open(bench_path, "w") as f:
                json.dump(b_list, f, indent=2)
            print(f"Appended GraphSAGE results to {bench_path}")

        return sage_results


def run_gnn_pipeline():
    trainer = GraphSAGETrainer()
    trainer.prepare_graph_data()
    return trainer.train_and_evaluate(epochs=25, lr=0.005)


if __name__ == "__main__":
    run_gnn_pipeline()

