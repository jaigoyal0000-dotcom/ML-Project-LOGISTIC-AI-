"""
src/graph_builder.py
--------------------
Graph Construction, Stratified Corridor Edge Weighting, Centrality Analysis,
and Chokepoint Bottleneck Auditing for Delhivery Logistics Network.
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
import networkx as nx


class LogisticsNetworkGraph:
    """
    Constructs and analyzes a Directed Weighted Graph of Delhivery logistics facilities and corridors.
    Strictly uses training set data to compute historical corridor edge weights and centrality,
    preventing any target leakage into the test set.
    """

    def __init__(self, data_filepath="data/cleaned_segments.csv"):
        self.data_filepath = data_filepath
        self.df = None
        self.train_df = None
        self.test_df = None
        self.graph = None
        self.node_metrics_df = None
        self.corridor_metrics_df = None
        self.stratified_corridor_dict = {}
        self.global_median_delay_ratio = 1.0

    def load_data(self):
        print(f"Loading cleaned segment data from {self.data_filepath}...")
        self.df = pd.read_csv(self.data_filepath)
        self.train_df = self.df[self.df['data'] == 'training'].copy()
        self.test_df = self.df[self.df['data'] == 'test'].copy()
        self.global_median_delay_ratio = float(self.train_df['delay_ratio'].median())
        print(f"Loaded {len(self.df):,} total segments. Training: {len(self.train_df):,}, Test: {len(self.test_df):,}")
        print(f"Global historical training median delay ratio: {self.global_median_delay_ratio:.3f}")

    def build_graph(self):
        """
        Build directed weighted graph where edge weights capture the median actual-vs-OSRM
        delay ratio per corridor, stratified by route_type and time_of_day.
        """
        print("Constructing directed weighted network graph from training trips...")
        G = nx.DiGraph()

        # 1. Collect Hub Metadata (Names and States)
        hub_meta = {}
        for _, row in self.train_df.iterrows():
            src = row['source_center']
            dst = row['destination_center']
            if src not in hub_meta:
                hub_meta[src] = {
                    'center_id': src,
                    'name': row['source_name'],
                    'state': row['source_state']
                }
            if dst not in hub_meta:
                hub_meta[dst] = {
                    'center_id': dst,
                    'name': row['destination_name'],
                    'state': row['destination_state']
                }

        for node_id, meta in hub_meta.items():
            G.add_node(node_id, **meta)

        # 2. Compute Corridor-Level Aggregate Metrics on Training Data
        corridor_agg = self.train_df.groupby(['source_center', 'destination_center']).agg(
            trip_count=('trip_uuid', 'count'),
            median_delay_ratio=('delay_ratio', 'median'),
            mean_delay_ratio=('delay_ratio', 'mean'),
            median_actual_hr=('actual_time_hr', 'median'),
            median_osrm_hr=('osrm_time_hr', 'median'),
            median_distance_km=('actual_distance_km', 'median'),
            sla_breach_rate=('sla_breached', 'mean'),
            chronic_delay_rate=('is_chronic_delay', 'mean'),
            sla_breach_count=('sla_breached', 'sum')
        ).reset_index()

        # Flag chronically delayed corridors (>20% over OSRM, i.e., median_delay_ratio > 1.20)
        corridor_agg['is_chronically_delayed'] = corridor_agg['median_delay_ratio'] > 1.20

        # 3. Stratified weights by corridor, route_type and time_of_day
        stratified = self.train_df.groupby(
            ['source_center', 'destination_center', 'route_type', 'time_of_day']
        )['delay_ratio'].median().reset_index()

        for _, row in stratified.iterrows():
            key = (row['source_center'], row['destination_center'], row['route_type'], row['time_of_day'])
            self.stratified_corridor_dict[key] = float(row['delay_ratio'])

        # 4. Add Directed Weighted Edges to Graph
        for _, row in corridor_agg.iterrows():
            u = row['source_center']
            v = row['destination_center']
            weight = float(row['median_delay_ratio'])
            
            G.add_edge(
                u, v,
                weight=weight,
                median_delay_ratio=weight,
                trip_count=int(row['trip_count']),
                median_actual_hr=float(row['median_actual_hr']),
                median_osrm_hr=float(row['median_osrm_hr']),
                median_distance_km=float(row['median_distance_km']),
                sla_breach_rate=float(row['sla_breach_rate']),
                sla_breach_count=int(row['sla_breach_count']),
                is_chronically_delayed=bool(row['is_chronically_delayed'])
            )

        self.graph = G
        self.corridor_metrics_df = corridor_agg
        print(f"Graph constructed successfully: {G.number_of_nodes():,} Hubs (Nodes), {G.number_of_edges():,} Corridors (Edges).")
        print(f"Chronically delayed corridors (>20% delay): {corridor_agg['is_chronically_delayed'].sum():,} / {len(corridor_agg):,} ({corridor_agg['is_chronically_delayed'].mean()*100:.1f}%)")
        return G

    def compute_network_metrics(self):
        """
        Compute In-Degree, Out-Degree, Betweenness Centrality, and Clustering Coefficient.
        Rank hubs by structural chokepoint severity and SLA breach contribution.
        """
        print("Computing network topology measures (Degree, Centrality, Clustering)...")
        G = self.graph

        # Degree measures
        in_degrees = dict(G.in_degree())
        out_degrees = dict(G.out_degree())
        total_degrees = {n: in_degrees.get(n, 0) + out_degrees.get(n, 0) for n in G.nodes()}

        # Betweenness Centrality (approximated k=200 if large for speed, or exact if manageable)
        num_nodes = G.number_of_nodes()
        k_sample = min(250, num_nodes) if num_nodes > 300 else None
        print(f"Computing betweenness centrality (k_sample={k_sample})...")
        betweenness = nx.betweenness_centrality(G, weight=None, normalized=True, k=k_sample, seed=42)

        # Clustering coefficient (directed)
        print("Computing directed clustering coefficients...")
        clustering = nx.clustering(G)

        # Hub SLA breach volume from training trips
        src_breaches = self.train_df.groupby('source_center')['sla_breached'].agg(['count', 'sum']).rename(
            columns={'count': 'outbound_trip_vol', 'sum': 'outbound_sla_breaches'}
        )
        dst_breaches = self.train_df.groupby('destination_center')['sla_breached'].agg(['count', 'sum']).rename(
            columns={'count': 'inbound_trip_vol', 'sum': 'inbound_sla_breaches'}
        )

        # Combine into DataFrame
        node_records = []
        for n in G.nodes():
            meta = G.nodes[n]
            in_deg = in_degrees.get(n, 0)
            out_deg = out_degrees.get(n, 0)
            tot_deg = total_degrees.get(n, 0)
            bc = betweenness.get(n, 0.0)
            cc = clustering.get(n, 0.0)

            out_vol = src_breaches.loc[n, 'outbound_trip_vol'] if n in src_breaches.index else 0
            out_brk = src_breaches.loc[n, 'outbound_sla_breaches'] if n in src_breaches.index else 0
            in_vol = dst_breaches.loc[n, 'inbound_trip_vol'] if n in dst_breaches.index else 0
            in_brk = dst_breaches.loc[n, 'inbound_sla_breaches'] if n in dst_breaches.index else 0

            total_vol = out_vol + in_vol
            total_breaches = out_brk + in_brk
            hub_breach_rate = (total_breaches / total_vol) if total_vol > 0 else 0.0

            # Average outbound delay ratio on incident edges
            out_edges = G.out_edges(n, data=True)
            if out_edges:
                avg_out_delay = np.median([d['median_delay_ratio'] for _, _, d in out_edges])
            else:
                avg_out_delay = self.global_median_delay_ratio

            node_records.append({
                'hub_id': n,
                'hub_name': meta.get('name', n),
                'hub_state': meta.get('state', 'Unknown'),
                'in_degree': in_deg,
                'out_degree': out_deg,
                'total_degree': tot_deg,
                'betweenness_centrality': bc,
                'clustering_coefficient': cc,
                'outbound_volume': out_vol,
                'inbound_volume': in_vol,
                'total_volume': total_vol,
                'outbound_sla_breaches': out_brk,
                'inbound_sla_breaches': in_brk,
                'total_sla_breaches': total_breaches,
                'hub_sla_breach_rate': hub_breach_rate,
                'avg_outbound_delay_ratio': avg_out_delay
            })

        metrics_df = pd.DataFrame(node_records)

        # Normalized Composite Chokepoint Risk Score (0 to 100)
        # Combines network betweenness centrality, total volume handled, and SLA breach contribution
        bc_norm = (metrics_df['betweenness_centrality'] - metrics_df['betweenness_centrality'].min()) / (
            metrics_df['betweenness_centrality'].max() - metrics_df['betweenness_centrality'].min() + 1e-9
        )
        vol_norm = (metrics_df['total_volume'] - metrics_df['total_volume'].min()) / (
            metrics_df['total_volume'].max() - metrics_df['total_volume'].min() + 1e-9
        )
        brk_norm = (metrics_df['total_sla_breaches'] - metrics_df['total_sla_breaches'].min()) / (
            metrics_df['total_sla_breaches'].max() - metrics_df['total_sla_breaches'].min() + 1e-9
        )
        delay_norm = np.clip(metrics_df['avg_outbound_delay_ratio'] / 2.0, 0, 1)

        metrics_df['chokepoint_risk_score'] = (
            0.35 * bc_norm + 0.30 * brk_norm + 0.20 * vol_norm + 0.15 * delay_norm
        ) * 100.0

        metrics_df = metrics_df.sort_values(by='chokepoint_risk_score', ascending=False).reset_index(drop=True)
        self.node_metrics_df = metrics_df

        print("\n=== TOP 5 BOTTLENECK CHOKEPOINT HUBS ===")
        top5 = metrics_df.head(5)[
            ['hub_id', 'hub_name', 'hub_state', 'betweenness_centrality', 'total_sla_breaches', 'total_volume', 'chokepoint_risk_score']
        ]
        print(top5.to_string(index=False))

        return metrics_df

    def get_corridor_feature(self, source_id, dest_id, route_type, time_of_day):
        """
        Lookup historical training corridor delay ratio.
        Fallbacks to corridor overall median -> source outbound median -> global median.
        """
        strat_key = (source_id, dest_id, route_type, time_of_day)
        if strat_key in self.stratified_corridor_dict:
            return self.stratified_corridor_dict[strat_key]

        if self.graph and self.graph.has_edge(source_id, dest_id):
            return self.graph[source_id][dest_id]['median_delay_ratio']

        # Fallback to source node average outbound delay
        if self.node_metrics_df is not None:
            match = self.node_metrics_df[self.node_metrics_df['hub_id'] == source_id]
            if not match.empty:
                return float(match.iloc[0]['avg_outbound_delay_ratio'])

        return self.global_median_delay_ratio

    def save_artifacts(self, output_dir="data"):
        os.makedirs(output_dir, exist_ok=True)
        # Save node metrics
        node_csv = os.path.join(output_dir, "hub_centrality_metrics.csv")
        self.node_metrics_df.to_csv(node_csv, index=False)
        print(f"Saved hub centrality metrics to {node_csv}")

        # Save corridor metrics
        corr_csv = os.path.join(output_dir, "corridor_metrics.csv")
        self.corridor_metrics_df.to_csv(corr_csv, index=False)
        print(f"Saved corridor metrics to {corr_csv}")

        # Save graph object
        graph_pkl = os.path.join(output_dir, "logistics_graph.pkl")
        with open(graph_pkl, "wb") as f:
            pickle.dump({
                'graph': self.graph,
                'stratified_corridor_dict': self.stratified_corridor_dict,
                'global_median_delay_ratio': self.global_median_delay_ratio
            }, f)
        print(f"Saved logistics graph object to {graph_pkl}")


def run_graph_pipeline():
    net = LogisticsNetworkGraph()
    net.load_data()
    net.build_graph()
    net.compute_network_metrics()
    net.save_artifacts()
    return net


if __name__ == "__main__":
    run_graph_pipeline()

