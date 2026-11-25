"""
src/visualize.py
----------------
Generates publication-quality charts and network diagrams saved to reports/figures/.
Essential for inclusion in PowerPoint slides, academic papers, and consulting memos.
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx

# Styling configuration
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#CCCCCC'
plt.rcParams['axes.linewidth'] = 0.8


def generate_all_figures(output_dir="reports/figures"):
    os.makedirs(output_dir, exist_ok=True)
    print(f"Generating publication figures to {output_dir}...")

    # Load data
    segments = pd.read_csv("data/cleaned_segments.csv")
    hubs = pd.read_csv("data/hub_centrality_metrics.csv")
    corridors = pd.read_csv("data/corridor_metrics.csv")
    rules = pd.read_csv("data/ftl_vs_carting_rules.csv")
    with open("models/benchmark_results.json", "r") as f:
        benchmarks = json.load(f)

    # -------------------------------------------------------------
    # FIGURE 1: OSRM Underestimation & Delay Ratio Distribution
    # -------------------------------------------------------------
    print("Generating Figure 1: Delay Ratio Distribution...")
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    plot_df = segments[segments['delay_ratio'] <= 4.0]

    sns.histplot(
        data=plot_df,
        x="delay_ratio",
        hue="route_type",
        bins=40,
        kde=True,
        palette={"FTL": "#1E3A8A", "Carting": "#EA580C"},
        alpha=0.45,
        ax=ax
    )
    median_val = segments['delay_ratio'].median()
    ax.axvline(1.0, color='green', linestyle='--', linewidth=2, label="OSRM Baseline (1.0x)")
    ax.axvline(1.2, color='red', linestyle=':', linewidth=2, label="Chronic Delay Threshold (1.2x)")
    ax.axvline(median_val, color='#7C3AED', linestyle='-', linewidth=2.5, label=f"Observed Median ({median_val:.2f}x)")

    ax.set_title("Delhivery National Freight: Actual vs. OSRM Travel Time Ratio", fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel("Delay Ratio (Actual Moving Time / OSRM Estimated Time)", fontsize=11)
    ax.set_ylabel("Shipment Segment Count", fontsize=11)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9)
    plt.tight_layout()
    f1_path = os.path.join(output_dir, "fig1_osrm_delay_distribution.png")
    plt.savefig(f1_path)
    plt.close()

    # -------------------------------------------------------------
    # FIGURE 2: Top 10 Chokepoint Hubs Leaderboard
    # -------------------------------------------------------------
    print("Generating Figure 2: Top Chokepoints...")
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    top10 = hubs.head(10).sort_values('chokepoint_risk_score', ascending=True)

    # Clean display labels
    clean_labels = [f"{r['hub_name'].split('_')[0]} ({r['hub_state']})" for _, r in top10.iterrows()]
    colors = plt.cm.plasma(np.linspace(0.2, 0.85, len(top10)))

    bars = ax.barh(clean_labels, top10['chokepoint_risk_score'], color=colors, height=0.65, edgecolor='black', linewidth=0.5)

    for bar, (_, r) in zip(bars, top10.iterrows()):
        ax.text(
            bar.get_width() + 1.2, bar.get_y() + bar.get_height()/2,
            f"Breaches: {int(r['total_sla_breaches']):,} | BC: {r['betweenness_centrality']:.3f}",
            va='center', fontsize=9, fontweight='medium', color='#333333'
        )

    ax.set_xlim(0, 115)
    ax.set_title("Top 10 National Logistics Chokepoints (Composite Risk Score / 100)", fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel("Chokepoint Risk Score (Betweenness + Volume + SLA Breaches)", fontsize=11)
    plt.tight_layout()
    f2_path = os.path.join(output_dir, "fig2_top_chokepoints_sla_breaches.png")
    plt.savefig(f2_path)
    plt.close()

    # -------------------------------------------------------------
    # FIGURE 3: Logistics Network Topology & Chokepoints Graph
    # -------------------------------------------------------------
    print("Generating Figure 3: Network Topology Graph...")
    with open("data/logistics_graph.pkl", "rb") as f:
        graph_obj = pickle.load(f)
    G = graph_obj['graph']

    # Sample sub-network of top 40 hubs for crisp visual representation
    top40_nodes = hubs.head(40)['hub_id'].tolist()
    sub_G = G.subgraph(top40_nodes)

    fig, ax = plt.subplots(figsize=(11, 8), dpi=300)
    pos = nx.spring_layout(sub_G, seed=42, k=0.55)

    # Node sizes based on degree
    node_sizes = [hubs.loc[hubs['hub_id'] == n, 'total_volume'].values[0] * 1.2 if n in hubs['hub_id'].values else 150 for n in sub_G.nodes()]
    node_sizes = np.clip(node_sizes, 100, 2000)

    # Edge colors based on delay
    edge_colors = ['#EF4444' if sub_G[u][v].get('is_chronically_delayed', False) else '#10B981' for u, v in sub_G.edges()]

    nx.draw_networkx_nodes(sub_G, pos, node_size=node_sizes, node_color='#1E3A8A', alpha=0.85, ax=ax)
    nx.draw_networkx_edges(sub_G, pos, edge_color=edge_colors, width=1.2, arrowsize=10, alpha=0.6, ax=ax)

    # Label top 7 hubs
    labels = {}
    for n in hubs.head(7)['hub_id']:
        if n in sub_G:
            name = hubs.loc[hubs['hub_id'] == n, 'hub_name'].values[0]
            labels[n] = name.split('_')[0]

    nx.draw_networkx_labels(sub_G, pos, labels=labels, font_size=9, font_weight='bold', font_color='#FFFFFF', ax=ax,
                            bbox=dict(boxstyle="round,pad=0.2", fc="#DC2626", ec="black", lw=0.5, alpha=0.9))

    ax.set_title("Logistics Network Topology (Red Edges = Chronic Delay >1.2x | Red Badges = Top Chokepoints)", fontsize=12, fontweight='bold', pad=12)
    ax.axis('off')
    plt.tight_layout()
    f3_path = os.path.join(output_dir, "fig3_network_topology_bottlenecks.png")
    plt.savefig(f3_path)
    plt.close()

    # -------------------------------------------------------------
    # FIGURE 4: Model Benchmarking - The Graph Advantage
    # -------------------------------------------------------------
    print("Generating Figure 4: Model Benchmarks...")
    bench_df = pd.DataFrame(benchmarks)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)

    # Shorten names for plotting
    short_names = [
        "OSRM Routing", "Baseline: Linear", "Baseline: GBM",
        "Graph: RF Regressor", "Graph: GBM Regressor", "Graph: Deep GraphSAGE"
    ][:len(bench_df)]
    bench_df['ShortName'] = short_names

    # MAE Chart
    colors_mae = ['#9CA3AF', '#60A5FA', '#3B82F6', '#10B981', '#059669', '#15803D'][:len(bench_df)]
    bars1 = ax1.bar(bench_df['ShortName'], bench_df['MAE (Minutes)'], color=colors_mae, width=0.55, edgecolor='black', lw=0.5)
    for b in bars1:
        ax1.text(b.get_x() + b.get_width()/2, b.get_height() + 1.5, f"{b.get_height():.1f}m", ha='center', fontsize=9, fontweight='bold')
    ax1.set_title("Mean Absolute Error (Minutes) - Lower is Better", fontsize=12, fontweight='bold', pad=10)
    ax1.set_ylabel("MAE (Minutes)", fontsize=10)
    ax1.tick_params(axis='x', rotation=30)
    ax1.set_ylim(0, max(bench_df['MAE (Minutes)']) * 1.15)

    # Within-15% Accuracy Chart
    colors_acc = ['#EF4444', '#F59E0B', '#3B82F6', '#8B5CF6', '#1E3A8A', '#4338CA'][:len(bench_df)]
    bars2 = ax2.bar(bench_df['ShortName'], bench_df['Within-15% Accuracy (%)'], color=colors_acc, width=0.55, edgecolor='black', lw=0.5)
    for b in bars2:
        ax2.text(b.get_x() + b.get_width()/2, b.get_height() + 1.2, f"{b.get_height():.1f}%", ha='center', fontsize=9, fontweight='bold')
    ax2.set_title("Within-15% Prediction Accuracy (%) - Higher is Better", fontsize=12, fontweight='bold', pad=10)
    ax2.set_ylabel("Trips within ±15% of Actual (%)", fontsize=10)
    ax2.tick_params(axis='x', rotation=30)
    ax2.set_ylim(0, max(bench_df['Within-15% Accuracy (%)']) * 1.2)

    plt.suptitle("Algorithmic Benchmark: Trip-Level vs. Graph-Enhanced Predictions", fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    f4_path = os.path.join(output_dir, "fig4_graph_advantage_benchmarks.png")
    plt.savefig(f4_path)
    plt.close()

    # -------------------------------------------------------------
    # FIGURE 5: FTL vs. Carting Trade-offs
    # -------------------------------------------------------------
    print("Generating Figure 5: FTL vs. Carting Trade-offs...")
    fig, (ax_t, ax_c) = plt.subplots(1, 2, figsize=(13, 5), dpi=300)

    # Delivery time comparison
    x = np.arange(len(rules))
    w = 0.35
    ax_t.bar(x - w/2, rules['FTL Median Time (hr)'], width=w, label='FTL (Dedicated)', color='#1E3A8A', edgecolor='black', lw=0.5)
    ax_t.bar(x + w/2, rules['Carting Median Time (hr)'], width=w, label='Carting (Consolidated)', color='#F59E0B', edgecolor='black', lw=0.5)
    ax_t.set_xticks(x)
    labels_clean = [f"{r['Distance Band'].split(' ')[0]}\n{r['Source Hub Risk'].split(' ')[0]}" for _, r in rules.iterrows()]
    ax_t.set_xticklabels(labels_clean, rotation=45, fontsize=8)
    ax_t.set_title("Transit Time: FTL vs. Carting (Hours)", fontsize=11, fontweight='bold', pad=10)
    ax_t.set_ylabel("Median Transit Time (Hours)", fontsize=10)
    ax_t.legend()

    # Total Cost comparison
    ax_c.bar(x - w/2, rules['FTL Total Cost (INR)'], width=w, label='FTL Cost', color='#1E3A8A', edgecolor='black', lw=0.5)
    ax_c.bar(x + w/2, rules['Carting Total Cost (INR)'], width=w, label='Carting Cost', color='#10B981', edgecolor='black', lw=0.5)
    ax_c.set_xticks(x)
    ax_c.set_xticklabels(labels_clean, rotation=45, fontsize=8)
    ax_c.set_title("Economic Cost: Base Tariff + SLA Risk (INR)", fontsize=11, fontweight='bold', pad=10)
    ax_c.set_ylabel("Total Economic Cost (INR)", fontsize=10)
    ax_c.legend()

    plt.suptitle("FTL vs. Carting Decision Framework: Time and Cost Trade-Offs", fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    f5_path = os.path.join(output_dir, "fig5_ftl_vs_carting_tradeoff.png")
    plt.savefig(f5_path)
    plt.close()

    print(f"All 5 publication figures successfully saved to {output_dir}/.")


if __name__ == "__main__":
    generate_all_figures()

