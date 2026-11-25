"""
src/route_optimizer.py
----------------------
Dynamic Chokepoint-Bypass Routing Engine.
Uses graph search algorithms on congestion-weighted edge penalties to discover
optimal alternative paths that bypass heavily congested national chokepoint hubs.
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
import networkx as nx


class DynamicRouteOptimizer:
    def __init__(self,
                 graph_path="data/logistics_graph.pkl",
                 hubs_path="data/hubs_geocoded.csv"):
        self.graph_path = graph_path
        self.hubs_path = hubs_path
        self.G = None
        self.hubs_df = None
        self.hub_info = {}

    def load_network(self):
        with open(self.graph_path, "rb") as f:
            data = pickle.load(f)
        self.G = data['graph']

        if os.path.exists(self.hubs_path):
            self.hubs_df = pd.read_csv(self.hubs_path)
        else:
            self.hubs_df = pd.read_csv("data/hub_centrality_metrics.csv")

        self.hub_info = self.hubs_df.set_index('hub_id').to_dict('index')

    def find_routes(self, origin_id, destination_id, avoid_chokepoints=True):
        """
        Calculates:
        1. Direct / Shortest Distance Route
        2. Congestion-Aware Dynamic Bypass Route
        """
        if self.G is None:
            self.load_network()

        # Build undirected graph view with dual edge weights for routing
        routing_graph_distance = nx.Graph()
        routing_graph_congestion = nx.Graph()

        for u, v, data in self.G.edges(data=True):
            dist = float(data.get('median_distance_km', 50.0))
            delay_ratio = float(data.get('median_delay_ratio', 1.88))
            is_chronic = data.get('is_chronically_delayed', False)

            v_choke = self.hub_info.get(v, {}).get('chokepoint_risk_score', 20.0)
            u_choke = self.hub_info.get(u, {}).get('chokepoint_risk_score', 20.0)

            # Weight 1: Pure Geometric Distance
            routing_graph_distance.add_edge(u, v, weight=max(1.0, dist), dist=dist, delay=delay_ratio)

            # Weight 2: Congestion-Weighted Impedance Cost
            # Exponentially penalizes chronic delays and severe chokepoints
            choke_factor = 1.0 + (max(u_choke, v_choke) / 50.0)
            delay_penalty = (delay_ratio ** 1.6)
            congestion_cost = dist * delay_penalty * choke_factor

            routing_graph_congestion.add_edge(
                u, v,
                weight=congestion_cost,
                dist=dist,
                delay=delay_ratio,
                is_chronic=is_chronic
            )

        # 1. Standard Distance Path
        try:
            dist_path = nx.shortest_path(routing_graph_distance, source=origin_id, target=destination_id, weight='weight')
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            dist_path = [origin_id, destination_id]

        # 2. Congestion-Aware Path
        try:
            bypass_path = nx.shortest_path(routing_graph_congestion, source=origin_id, target=destination_id, weight='weight')
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            bypass_path = dist_path

        def summarize_path(path):
            total_dist = 0.0
            total_time_hr = 0.0
            hops = []
            chokepoints_encountered = []

            for i in range(len(path) - 1):
                u = path[i]
                v = path[i+1]
                u_name = self.hub_info.get(u, {}).get('hub_name', u).split(' (')[0]
                v_name = self.hub_info.get(v, {}).get('hub_name', v).split(' (')[0]

                if self.G.has_edge(u, v):
                    edge_d = self.G[u][v]
                    d_km = float(edge_d.get('median_distance_km', 60.0))
                    d_rat = float(edge_d.get('median_delay_ratio', 1.88))
                    t_hr = float(edge_d.get('median_actual_hr', (d_km / 50.0) * d_rat))
                elif self.G.has_edge(v, u):
                    edge_d = self.G[v][u]
                    d_km = float(edge_d.get('median_distance_km', 60.0))
                    d_rat = float(edge_d.get('median_delay_ratio', 1.88))
                    t_hr = float(edge_d.get('median_actual_hr', (d_km / 50.0) * d_rat))
                else:
                    d_km = 80.0
                    d_rat = 1.88
                    t_hr = (d_km / 50.0) * d_rat

                total_dist += d_km
                total_time_hr += t_hr

                u_choke = self.hub_info.get(u, {}).get('chokepoint_risk_score', 0)
                if u_choke > 60:
                    chokepoints_encountered.append(u_name)

                hops.append({
                    'from': u_name,
                    'to': v_name,
                    'distance_km': round(d_km, 1),
                    'delay_ratio': round(d_rat, 2),
                    'expected_time_hr': round(t_hr, 2)
                })

            v_last_choke = self.hub_info.get(path[-1], {}).get('chokepoint_risk_score', 0)
            if v_last_choke > 60:
                chokepoints_encountered.append(self.hub_info.get(path[-1], {}).get('hub_name', path[-1]).split(' (')[0])

            sla_risk = "High" if len(chokepoints_encountered) > 0 or total_time_hr > (total_dist / 40.0) else "Low"

            return {
                'path_nodes': path,
                'hop_count': len(path) - 1,
                'total_distance_km': round(total_dist, 1),
                'expected_transit_hr': round(total_time_hr, 2),
                'chokepoints_hit': list(set(chokepoints_encountered)),
                'sla_risk': sla_risk,
                'hops': hops
            }

        std_summary = summarize_path(dist_path)
        bypass_summary = summarize_path(bypass_path)

        # Calculate comparative advantage
        time_saved = max(0.0, std_summary['expected_transit_hr'] - bypass_summary['expected_transit_hr'])
        dist_diff = bypass_summary['total_distance_km'] - std_summary['total_distance_km']

        return {
            'origin_hub': self.hub_info.get(origin_id, {}).get('hub_name', origin_id),
            'destination_hub': self.hub_info.get(destination_id, {}).get('hub_name', destination_id),
            'standard_route': std_summary,
            'dynamic_bypass_route': bypass_summary,
            'hours_saved': round(time_saved, 2),
            'distance_delta_km': round(dist_diff, 1),
            'recommendation': "Bypass Route" if time_saved > 0.5 or (len(std_summary['chokepoints_hit']) > len(bypass_summary['chokepoints_hit'])) else "Standard Route"
        }


if __name__ == "__main__":
    opt = DynamicRouteOptimizer()
    opt.load_network()
    # Test sample route: Gurgaon Bilaspur to Bangalore Nelamangala
    res = opt.find_routes("IND000000ACB", "IND562132AAA")
    print("Origin:", res['origin_hub'])
    print("Destination:", res['destination_hub'])
    print("Standard Route Time:", res['standard_route']['expected_transit_hr'], "hrs | Chokepoints Hit:", res['standard_route']['chokepoints_hit'])
    print("Bypass Route Time:", res['dynamic_bypass_route']['expected_transit_hr'], "hrs | Chokepoints Hit:", res['dynamic_bypass_route']['chokepoints_hit'])
    print("Recommendation:", res['recommendation'])
