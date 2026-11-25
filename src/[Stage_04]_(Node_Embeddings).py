"""
src/node_embeddings.py
----------------------
Node2Vec random-walk embedding generation and GraphSAGE neighborhood aggregation
for logistics hubs in the Delhivery network.
"""

import os
import random
import pickle
import numpy as np
import pandas as pd
import networkx as nx
from gensim.models import Word2Vec


class Node2VecLogisticsEmbedder:
    """
    Learns continuous vector representations (embeddings) for logistics hubs
    by sampling transition-weighted walks across the corridor network.
    """

    def __init__(self, dimensions=16, walk_length=15, num_walks=20, p=1.0, q=0.5, seed=42):
        self.dimensions = dimensions
        self.walk_length = walk_length
        self.num_walks = num_walks
        self.p = p # Return parameter
        self.q = q # In-out parameter (q < 1.0 biases towards structural BFS)
        self.seed = seed
        self.embeddings = {}
        self.model = None

    def _generate_walk(self, G, start_node):
        """Generate a single biased random walk starting from start_node."""
        walk = [str(start_node)]
        curr = start_node
        for _ in range(self.walk_length - 1):
            neighbors = list(G.successors(curr)) if G.is_directed() else list(G.neighbors(curr))
            if not neighbors:
                # If no outgoing edge, check undirected neighbors or stop
                neighbors = list(G.predecessors(curr)) if G.is_directed() else []
                if not neighbors:
                    break

            # Weighted transition probability based on corridor delay ratio
            weights = []
            for nbr in neighbors:
                if G.has_edge(curr, nbr):
                    w = G[curr][nbr].get('weight', 1.0)
                else:
                    w = 1.0
                weights.append(float(w))

            total_w = sum(weights)
            probs = [w / total_w for w in weights] if total_w > 0 else [1.0 / len(weights)] * len(weights)
            next_node = np.random.choice(neighbors, p=probs)
            walk.append(str(next_node))
            curr = next_node
        return walk

    def fit(self, G):
        """Fit Node2Vec on the NetworkX graph G."""
        print(f"Generating Node2Vec random walks (walk_length={self.walk_length}, num_walks={self.num_walks})...")
        np.random.seed(self.seed)
        random.seed(self.seed)

        nodes = list(G.nodes())
        walks = []
        for _ in range(self.num_walks):
            np.random.shuffle(nodes)
            for node in nodes:
                walk = self._generate_walk(G, node)
                walks.append(walk)

        print(f"Generated {len(walks):,} random walks. Training Word2Vec skip-gram model...")
        self.model = Word2Vec(
            sentences=walks,
            vector_size=self.dimensions,
            window=5,
            min_count=1,
            sg=1, # Skip-Gram
            workers=2,
            epochs=10,
            seed=self.seed
        )

        for node in G.nodes():
            s_node = str(node)
            if s_node in self.model.wv:
                self.embeddings[s_node] = self.model.wv[s_node]
            else:
                self.embeddings[s_node] = np.zeros(self.dimensions, dtype=np.float32)

        print(f"Trained Node2Vec embeddings for {len(self.embeddings):,} hubs with dim={self.dimensions}.")
        return self.embeddings

    def get_embedding(self, hub_id):
        """Lookup embedding for hub_id with zero-vector fallback for unseen hubs."""
        s_id = str(hub_id)
        if s_id in self.embeddings:
            return self.embeddings[s_id]
        return np.zeros(self.dimensions, dtype=np.float32)

    def save(self, filepath="data/node2vec_embeddings.pkl"):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            pickle.dump({
                'embeddings': self.embeddings,
                'dimensions': self.dimensions
            }, f)
        print(f"Saved Node2Vec embeddings to {filepath}")

    @classmethod
    def load(cls, filepath="data/node2vec_embeddings.pkl"):
        with open(filepath, "rb") as f:
            data = pickle.load(f)
        obj = cls(dimensions=data['dimensions'])
        obj.embeddings = data['embeddings']
        return obj


def compute_graphsage_neighborhood_features(G, node_metrics_df):
    """
    Computes GraphSAGE-style mean neighbor aggregations:
    - 1-hop neighbor average delay ratio
    - 1-hop neighbor average betweenness centrality
    - 1-hop neighbor average chokepoint risk score
    """
    print("Computing GraphSAGE 1-hop neighborhood aggregations...")
    metrics_map = node_metrics_df.set_index('hub_id').to_dict('index')

    graphsage_feats = {}
    for node in G.nodes():
        succs = list(G.successors(node))
        preds = list(G.predecessors(node))
        neighbors = list(set(succs + preds))

        if neighbors:
            nbr_delays = [metrics_map.get(nbr, {}).get('avg_outbound_delay_ratio', 1.88) for nbr in neighbors]
            nbr_bcs = [metrics_map.get(nbr, {}).get('betweenness_centrality', 0.0) for nbr in neighbors]
            nbr_chokes = [metrics_map.get(nbr, {}).get('chokepoint_risk_score', 10.0) for nbr in neighbors]

            graphsage_feats[node] = {
                'sage_nbr_mean_delay': float(np.mean(nbr_delays)),
                'sage_nbr_max_delay': float(np.max(nbr_delays)),
                'sage_nbr_mean_betweenness': float(np.mean(nbr_bcs)),
                'sage_nbr_mean_chokepoint': float(np.mean(nbr_chokes))
            }
        else:
            graphsage_feats[node] = {
                'sage_nbr_mean_delay': 1.88,
                'sage_nbr_max_delay': 1.88,
                'sage_nbr_mean_betweenness': 0.0,
                'sage_nbr_mean_chokepoint': 10.0
            }

    sage_df = pd.DataFrame.from_dict(graphsage_feats, orient='index').reset_index().rename(columns={'index': 'hub_id'})
    out_csv = "data/graphsage_node_features.csv"
    sage_df.to_csv(out_csv, index=False)
    print(f"Saved GraphSAGE neighborhood features to {out_csv}")
    return sage_df


def run_embedding_pipeline():
    with open("data/logistics_graph.pkl", "rb") as f:
        graph_data = pickle.load(f)
    G = graph_data['graph']

    node_metrics_df = pd.read_csv("data/hub_centrality_metrics.csv")

    embedder = Node2VecLogisticsEmbedder(dimensions=16, walk_length=15, num_walks=20)
    embedder.fit(G)
    embedder.save("data/node2vec_embeddings.pkl")

    compute_graphsage_neighborhood_features(G, node_metrics_df)


if __name__ == "__main__":
    run_embedding_pipeline()

