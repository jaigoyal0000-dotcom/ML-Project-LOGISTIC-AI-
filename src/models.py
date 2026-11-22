"""
src/models.py
-------------
Trains, evaluates, and benchmarks Baseline vs. Graph-Enhanced ETA Prediction Models
for Delhivery Logistics. Strictly measures the 'Graph Advantage' on MAE and Within-15% Accuracy.
"""

import os
import json
import time
import pickle
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib


def compute_within_pct_accuracy(y_true, y_pred, pct=0.15):
    """
    Computes percentage of predictions falling within +/- pct of the actual value.
    Explicitly requested business metric in the IIT Guwahati / Delhivery challenge.
    """
    y_true = np.asarray(y_true, dtype=np.float64)
    y_pred = np.asarray(y_pred, dtype=np.float64)
    # Avoid zero division
    denom = np.where(y_true == 0, 1e-6, y_true)
    rel_error = np.abs(y_pred - y_true) / np.abs(denom)
    return float(np.mean(rel_error <= pct) * 100.0)


class ETAPredictionPipeline:
    def __init__(self, data_path="data/cleaned_segments.csv"):
        self.data_path = data_path
        self.df = None
        self.train_df = None
        self.test_df = None
        self.hub_metrics = None
        self.sage_metrics = None
        self.node2vec_data = None
        self.graph_data = None
        self.models = {}
        self.results = {}
        self.feature_names_baseline = []
        self.feature_names_graph = []

    def load_all_data(self):
        print("Loading prepared datasets and network representations...")
        self.df = pd.read_csv(self.data_path)
        self.hub_metrics = pd.read_csv("data/hub_centrality_metrics.csv").set_index('hub_id')
        self.sage_metrics = pd.read_csv("data/graphsage_node_features.csv").set_index('hub_id')

        with open("data/node2vec_embeddings.pkl", "rb") as f:
            self.node2vec_data = pickle.load(f)

        with open("data/logistics_graph.pkl", "rb") as f:
            self.graph_data = pickle.load(f)

        self.train_df = self.df[self.df['data'] == 'training'].copy()
        self.test_df = self.df[self.df['data'] == 'test'].copy()
        print(f"Loaded {len(self.train_df):,} training samples and {len(self.test_df):,} test samples.")

    def _extract_features_for_df(self, input_df, is_training=False):
        """Constructs both Baseline and Graph-Enhanced feature matrices."""
        strat_dict = self.graph_data['stratified_corridor_dict']
        global_median = self.graph_data['global_median_delay_ratio']
        embeddings = self.node2vec_data['embeddings']
        emb_dim = self.node2vec_data['dimensions']

        # 1. Baseline Features (trip-level only)
        base_records = []
        graph_records = []

        hub_dict = self.hub_metrics.to_dict('index')
        sage_dict = self.sage_metrics.to_dict('index')

        for _, row in input_df.iterrows():
            src = row['source_center']
            dst = row['destination_center']
            rtype = row['route_type']
            tod = row['time_of_day']
            osrm_t = float(row['osrm_time_hr'])
            osrm_d = float(row['osrm_distance_km'])
            hr = int(row['start_hour'])
            dow = int(row['start_dayofweek'])
            is_weekend = 1 if dow in [5, 6] else 0
            is_ftl = 1 if rtype == 'FTL' else 0

            # Baseline vector
            b_feat = [
                osrm_t,
                osrm_d,
                is_ftl,
                hr,
                dow,
                is_weekend,
                1 if tod == 'Morning' else 0,
                1 if tod == 'Afternoon' else 0,
                1 if tod == 'Evening' else 0,
                1 if tod == 'Night' else 0,
                1 if osrm_d < 100 else 0,
                1 if 100 <= osrm_d <= 300 else 0,
                1 if osrm_d > 300 else 0,
            ]
            base_records.append(b_feat)

            # 2. Graph Corridor Weight (Stratified lookup with fallback)
            corr_key = (src, dst, rtype, tod)
            if corr_key in strat_dict:
                corr_weight = strat_dict[corr_key]
            elif self.graph_data['graph'].has_edge(src, dst):
                corr_weight = self.graph_data['graph'][src][dst].get('median_delay_ratio', global_median)
            else:
                corr_weight = global_median

            corr_chronic = 1 if corr_weight > 1.20 else 0

            # Centrality metrics lookup
            src_m = hub_dict.get(src, {})
            dst_m = hub_dict.get(dst, {})

            src_bc = float(src_m.get('betweenness_centrality', 0.0))
            dst_bc = float(dst_m.get('betweenness_centrality', 0.0))
            src_in_deg = float(src_m.get('in_degree', 0.0))
            src_out_deg = float(src_m.get('out_degree', 0.0))
            dst_in_deg = float(dst_m.get('in_degree', 0.0))
            dst_out_deg = float(dst_m.get('out_degree', 0.0))
            src_cc = float(src_m.get('clustering_coefficient', 0.0))
            dst_cc = float(dst_m.get('clustering_coefficient', 0.0))
            src_choke = float(src_m.get('chokepoint_risk_score', 15.0))
            dst_choke = float(dst_m.get('chokepoint_risk_score', 15.0))
            src_brk_rate = float(src_m.get('hub_sla_breach_rate', 0.88))
            dst_brk_rate = float(dst_m.get('hub_sla_breach_rate', 0.88))

            # GraphSAGE neighborhood features
            src_s = sage_dict.get(src, {})
            dst_s = sage_dict.get(dst, {})
            src_sage_delay = float(src_s.get('sage_nbr_mean_delay', 1.88))
            dst_sage_delay = float(dst_s.get('sage_nbr_mean_delay', 1.88))
            src_sage_choke = float(src_s.get('sage_nbr_mean_chokepoint', 15.0))
            dst_sage_choke = float(dst_s.get('sage_nbr_mean_chokepoint', 15.0))

            # Node2Vec embeddings
            src_emb = embeddings.get(str(src), np.zeros(emb_dim, dtype=np.float32))
            dst_emb = embeddings.get(str(dst), np.zeros(emb_dim, dtype=np.float32))

            norm_src = np.linalg.norm(src_emb)
            norm_dst = np.linalg.norm(dst_emb)
            cosine_sim = float(np.dot(src_emb, dst_emb) / (norm_src * norm_dst + 1e-9))
            euclid_dist = float(np.linalg.norm(src_emb - dst_emb))

            # Combine baseline + graph features
            g_feat = b_feat + [
                corr_weight,
                corr_chronic,
                src_bc,
                dst_bc,
                src_in_deg,
                src_out_deg,
                dst_in_deg,
                dst_out_deg,
                src_cc,
                dst_cc,
                src_choke,
                dst_choke,
                src_brk_rate,
                dst_brk_rate,
                src_sage_delay,
                dst_sage_delay,
                src_sage_choke,
                dst_sage_choke,
                cosine_sim,
                euclid_dist,
            ]
            # Add top embedding dimensions
            g_feat.extend(src_emb.tolist())
            g_feat.extend(dst_emb.tolist())

            graph_records.append(g_feat)

        if not self.feature_names_baseline:
            self.feature_names_baseline = [
                'osrm_time_hr', 'osrm_distance_km', 'is_ftl', 'start_hour', 'start_dayofweek', 'is_weekend',
                'tod_morning', 'tod_afternoon', 'tod_evening', 'tod_night',
                'dist_short', 'dist_medium', 'dist_long'
            ]
            self.feature_names_graph = self.feature_names_baseline + [
                'corr_delay_weight', 'corr_chronic_flag',
                'src_betweenness', 'dst_betweenness',
                'src_in_degree', 'src_out_degree', 'dst_in_degree', 'dst_out_degree',
                'src_clustering', 'dst_clustering',
                'src_chokepoint_risk', 'dst_chokepoint_risk',
                'src_hub_breach_rate', 'dst_hub_breach_rate',
                'src_sage_delay', 'dst_sage_delay',
                'src_sage_choke', 'dst_sage_choke',
                'emb_cosine_sim', 'emb_euclid_dist'
            ] + [f'src_emb_{i}' for i in range(emb_dim)] + [f'dst_emb_{i}' for i in range(emb_dim)]

        X_base = np.array(base_records, dtype=np.float32)
        X_graph = np.array(graph_records, dtype=np.float32)
        y = input_df['actual_time_hr'].values.astype(np.float32)

        return X_base, X_graph, y

    def train_and_benchmark(self):
        """Train baseline and graph models and compute all performance metrics."""
        print("Extracting feature matrices for Training and Test sets...")
        X_train_base, X_train_graph, y_train = self._extract_features_for_df(self.train_df, is_training=True)
        X_test_base, X_test_graph, y_test = self._extract_features_for_df(self.test_df, is_training=False)

        print(f"Baseline feature matrix shape: {X_train_base.shape}")
        print(f"Graph-enhanced feature matrix shape: {X_train_graph.shape}")

        # Models configurations
        models_to_run = {
            "OSRM Routing Engine (Reference)": {
                'type': 'osrm_ref',
                'features': 'none'
            },
            "Baseline: Linear Regression": {
                'model': Ridge(alpha=1.0),
                'features': 'base'
            },
            "Baseline: Gradient Boosting (Trip-Level Only)": {
                'model': GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42, learning_rate=0.1),
                'features': 'base'
            },
            "Graph-Enhanced: Random Forest Regressor": {
                'model': RandomForestRegressor(n_estimators=100, max_depth=12, min_samples_split=5, random_state=42, n_jobs=-1),
                'features': 'graph'
            },
            "Graph-Enhanced: Gradient Boosting (+ Network Intelligence)": {
                'model': GradientBoostingRegressor(n_estimators=150, max_depth=6, random_state=42, learning_rate=0.08),
                'features': 'graph'
            }
        }

        benchmarks = []
        osrm_pred_test = self.test_df['osrm_time_hr'].values

        for name, config in models_to_run.items():
            print(f"\n--- Evaluating {name} ---")
            t0 = time.time()

            if config.get('type') == 'osrm_ref':
                y_pred_test = osrm_pred_test
                y_pred_train = self.train_df['osrm_time_hr'].values
                train_time = 0.0
            else:
                mdl = config['model']
                is_graph = (config['features'] == 'graph')
                X_tr = X_train_graph if is_graph else X_train_base
                X_te = X_test_graph if is_graph else X_test_base

                print(f"Training on {len(X_tr):,} samples...")
                mdl.fit(X_tr, y_train)
                train_time = time.time() - t0
                y_pred_test = mdl.predict(X_te)
                y_pred_train = mdl.predict(X_tr)
                # Keep positive predictions
                y_pred_test = np.maximum(y_pred_test, 0.05)

                self.models[name] = mdl

            # Calculate Metrics on Test Set
            mae = float(mean_absolute_error(y_test, y_pred_test))
            rmse = float(np.sqrt(mean_squared_error(y_test, y_pred_test)))
            r2 = float(r2_score(y_test, y_pred_test))
            acc15 = compute_within_pct_accuracy(y_test, y_pred_test, pct=0.15)
            acc25 = compute_within_pct_accuracy(y_test, y_pred_test, pct=0.25)

            mae_min = mae * 60.0 # MAE in minutes

            result = {
                'Model': name,
                'MAE (Hours)': round(mae, 3),
                'MAE (Minutes)': round(mae_min, 1),
                'Within-15% Accuracy (%)': round(acc15, 2),
                'Within-25% Accuracy (%)': round(acc25, 2),
                'RMSE (Hours)': round(rmse, 3),
                'R² Score': round(r2, 3),
                'Training Time (s)': round(train_time, 2)
            }
            benchmarks.append(result)
            print(f"-> MAE: {mae:.3f} hrs ({mae_min:.1f} mins) | Within 15%: {acc15:.2f}% | R²: {r2:.3f}")

        bench_df = pd.DataFrame(benchmarks)

        # Calculate exact "Graph Advantage" over baseline
        base_mae = bench_df.loc[bench_df['Model'] == 'Baseline: Gradient Boosting (Trip-Level Only)', 'MAE (Hours)'].values[0]
        base_15 = bench_df.loc[bench_df['Model'] == 'Baseline: Gradient Boosting (Trip-Level Only)', 'Within-15% Accuracy (%)'].values[0]

        best_graph_mae = bench_df.loc[bench_df['Model'] == 'Graph-Enhanced: Gradient Boosting (+ Network Intelligence)', 'MAE (Hours)'].values[0]
        best_graph_15 = bench_df.loc[bench_df['Model'] == 'Graph-Enhanced: Gradient Boosting (+ Network Intelligence)', 'Within-15% Accuracy (%)'].values[0]

        mae_reduction = (base_mae - best_graph_mae) / base_mae * 100.0
        acc15_improvement = best_graph_15 - base_15

        print("\n=======================================================")
        print("          FINAL BENCHMARK COMPARISON MATRIX            ")
        print("=======================================================")
        print(bench_df.to_string(index=False))
        print("-------------------------------------------------------")
        print(f"THE GRAPH ADVANTAGE:")
        print(f" • MAE Reduction: {mae_reduction:.2f}% (from {base_mae:.3f}h down to {best_graph_mae:.3f}h)")
        print(f" • Within-15% Accuracy Gain: +{acc15_improvement:.2f}% points (from {base_15:.2f}% up to {best_graph_15:.2f}%)")
        print("=======================================================\n")

        # Feature Importance Analysis for the Best Graph Model
        best_model = self.models.get("Graph-Enhanced: Gradient Boosting (+ Network Intelligence)")
        if hasattr(best_model, "feature_importances_"):
            importances = best_model.feature_importances_
            feat_imp_df = pd.DataFrame({
                'feature': self.feature_names_graph,
                'importance': importances
            }).sort_values('importance', ascending=False).reset_index(drop=True)
            print("Top 10 Most Predictive Features in Graph-Enhanced Model:")
            print(feat_imp_df.head(10).to_string(index=False))
            os.makedirs("models", exist_ok=True)
            feat_imp_df.to_csv("models/feature_importance.csv", index=False)

        # Save artifacts
        os.makedirs("models", exist_ok=True)
        bench_df.to_json("models/benchmark_results.json", orient='records', indent=2)

        # Save the primary production model and transformer metadata
        joblib.dump(best_model, "models/best_graph_model.joblib")
        joblib.dump(self.models["Baseline: Gradient Boosting (Trip-Level Only)"], "models/baseline_model.joblib")

        pipeline_meta = {
            'feature_names_baseline': self.feature_names_baseline,
            'feature_names_graph': self.feature_names_graph,
            'mae_reduction_pct': mae_reduction,
            'acc15_gain_pts': acc15_improvement,
            'base_mae': base_mae,
            'best_graph_mae': best_graph_mae,
            'base_15': base_15,
            'best_graph_15': best_graph_15
        }
        with open("models/pipeline_meta.json", "w") as f:
            json.dump(pipeline_meta, f, indent=2)

        print("Models, metrics, and metadata successfully saved to models/.")
        return bench_df


def run_modeling_pipeline():
    pipe = ETAPredictionPipeline()
    pipe.load_all_data()
    return pipe.train_and_benchmark()


if __name__ == "__main__":
    run_modeling_pipeline()

