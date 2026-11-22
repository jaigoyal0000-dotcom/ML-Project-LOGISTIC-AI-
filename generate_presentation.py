"""
generate_presentation.py
------------------------
Generates a comprehensive 16-slide PowerPoint presentation deck (presentation_slides.pptx)
featuring extensive data breakdowns, empirical outputs, mathematical formulations,
and ROI calculations for Delhivery Logistics Network Intelligence.
"""

import os
import json
import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE


def build_powerpoint_deck(output_path="presentation_slides.pptx"):
    print(f"Creating expanded PowerPoint presentation at {output_path}...")
    prs = Presentation()
    prs.slide_width = Inches(13.333)  # 16:9 widescreen
    prs.slide_height = Inches(7.5)

    # Color Palette
    COLOR_PRIMARY = RGBColor(15, 23, 42)      # Deep Slate Navy (#0F172A)
    COLOR_BRAND = RGBColor(30, 58, 138)        # Royal Blue (#1E3A8A)
    COLOR_ACCENT = RGBColor(234, 88, 12)       # Energetic Orange (#EA580C)
    COLOR_CYAN = RGBColor(6, 182, 212)         # Electric Cyan (#06B6D4)
    COLOR_GREEN = RGBColor(16, 185, 129)       # Emerald (#10B981)
    COLOR_DARK = RGBColor(31, 41, 55)          # Charcoal (#1F2937)
    COLOR_MUTED = RGBColor(100, 116, 139)      # Slate Gray (#64748B)
    COLOR_CARD_BG = RGBColor(241, 245, 249)    # Light Slate Fill (#F1F5F9)
    COLOR_WHITE = RGBColor(255, 255, 255)

    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title_text, category="DELHIVERY LOGISTICS NETWORK INTELLIGENCE"):
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.1))
        tf = header_box.text_frame
        tf.word_wrap = True
        
        p_cat = tf.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_ACCENT
        
        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_BRAND

    def add_card(slide, left, top, width, height, title, items, bg_color=COLOR_CARD_BG):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = RGBColor(203, 213, 225)
        
        tb = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.15), width - Inches(0.3), height - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p0 = tf.paragraphs[0]
        p0.text = title
        p0.font.size = Pt(13)
        p0.font.bold = True
        p0.font.color.rgb = COLOR_BRAND
        p0.space_after = Pt(8)
        
        for head, body in items:
            p = tf.add_paragraph()
            p.text = f"• {head}: {body}" if head else f"• {body}"
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_DARK
            p.space_after = Pt(6)

    # -------------------------------------------------------------
    # SLIDE 1: Title Slide
    # -------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = COLOR_PRIMARY
    bg1.line.fill.background()

    t_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(4.0))
    tf1 = t_box.text_frame
    p1 = tf1.paragraphs[0]
    p1.text = "Optimizing Delivery ETAs with\nGraph-Based Network Intelligence"
    p1.font.size = Pt(38)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE

    p1_sub = tf1.add_paragraph()
    p1_sub.text = "Domain: Machine Learning · Graph Neural Networks · Predictive Logistics Analytics"
    p1_sub.font.size = Pt(18)
    p1_sub.font.color.rgb = COLOR_CYAN
    p1_sub.space_before = Pt(15)

    p1_auth = tf1.add_paragraph()
    p1_auth.text = "Industry Context: Delhivery Freight Network · Academic Major Project Defense"
    p1_auth.font.size = Pt(14)
    p1_auth.font.color.rgb = COLOR_ACCENT
    p1_auth.space_before = Pt(35)

    # -------------------------------------------------------------
    # SLIDE 2: Industry Problem & OSRM Failure
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "The Real-World Problem: Why OSRM Fails in Freight Logistics")

    tb2 = s2.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(6.2), Inches(5.3))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    bullets2 = [
        ("The Enterprise Context", "Delhivery operates India's largest freight network, moving millions of parcels daily through multi-hop hub-and-spoke journeys."),
        ("OSRM Routing Blindspot", "Delhivery uses OSRM (Open Source Routing Machine). OSRM assumes free-flow speed limits and shortest road distances, completely ignoring logistics realities."),
        ("The Empirical Deviation", "Audit of 144,867 scans reveals actual travel times are 1.88x longer than OSRM estimates (median delay of +88.3%)."),
        ("Cascading Dwell Queues", "Delays compound at intermediate sorting docks, cross-dock transfer hubs, and toll corridors."),
        ("Financial Penalty", "Unreliable ETAs trigger high SLA breach penalties, customer churn, and disrupted linehaul scheduling.")
    ]
    for i, (title, desc) in enumerate(bullets2):
        p = tf2.paragraphs[0] if i == 0 else tf2.add_paragraph()
        p.text = f"• {title}: {desc}"
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_DARK
        p.space_after = Pt(12)

    fig1 = "reports/figures/fig1_osrm_delay_distribution.png"
    if os.path.exists(fig1):
        s2.shapes.add_picture(fig1, Inches(7.2), Inches(1.8), width=Inches(5.3))

    # -------------------------------------------------------------
    # SLIDE 3: Dataset Architecture & Data Hygiene (NEW)
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Dataset Architecture & Data Hygiene Breakdown")

    # Table of Dataset Breakdown
    t_shape3 = s3.shapes.add_table(6, 4, Inches(0.8), Inches(1.6), Inches(6.5), Inches(2.6))
    tbl3 = t_shape3.table
    tbl_headers3 = ["Metric / Dimension", "Raw Dataset", "Cleaned Segments", "Partition Strategy"]
    for col_i, h in enumerate(tbl_headers3):
        c = tbl3.cell(0, col_i)
        c.text = h
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_BRAND
        for p in c.text_frame.paragraphs:
            p.font.bold = True
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_WHITE

    row_data3 = [
        ["Total Records", "144,867 scans", "26,214 corridor legs", "Zero-leakage split"],
        ["Unique Trips", "14,888 trips", "14,771 aggregated", "Chronological order"],
        ["Logistics Hubs", "1,589 facilities", "1,589 geocoded hubs", "Preserved topology"],
        ["Directed Corridors", "Overlapped scans", "2,501 discrete pairs", "Edge weights computed"],
        ["Train / Test Ratio", "Unstructured", "18,860 / 7,354", "72% Train / 28% Test"]
    ]
    for r_i, r in enumerate(row_data3, 1):
        for c_i, val in enumerate(r):
            c = tbl3.cell(r_i, c_i)
            c.text = val
            for p in c.text_frame.paragraphs:
                p.font.size = Pt(10)

    add_card(s3, Inches(7.5), Inches(1.6), Inches(5.0), Inches(5.2),
             "Data Hygiene & Leakage Prevention Rules",
             [
                 ("Temporal Partitioning", "Data is partitioned chronologically (older trips train the model, newer trips evaluate it). Avoids standard random shuffle leakage."),
                 ("Segment Synthesis", "Multi-scan raw waypoints are reconstructed into discrete Origin -> Destination corridor legs with clean duration metrics."),
                 ("Anomaly Filtering", "Filtered trips with negative durations, zero distances, or extreme sensor anomalies (>50x OSRM time)."),
                 ("No Target Information in Features", "Delay ratios and edge weights are strictly aggregated from training split data only; testing data never pollutes graph weights."),
                 ("Stratification", "Corridor delay metrics are stratified by Route Type (FTL vs. Carting) and Time-of-Day bins.")
             ])

    add_card(s3, Inches(0.8), Inches(4.5), Inches(6.5), Inches(2.3),
             "Core Features Extracted per Segment",
             [
                 ("Trip Features", "OSRM distance, OSRM duration, route type (FTL/Carting), hour of departure, day of week."),
                 ("Network Topological Features", "Origin betweenness, destination betweenness, origin in-degree, destination out-degree."),
                 ("Graph Embeddings", "16-D Node2Vec vector embeddings + 1-hop GraphSAGE neighborhood delay aggregations.")
             ])

    # -------------------------------------------------------------
    # SLIDE 4: Mathematical Formulations & Calculations (NEW)
    # -------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Mathematical Formulations & Network Calculus")

    add_card(s4, Inches(0.8), Inches(1.6), Inches(5.7), Inches(2.6),
             "1. Corridor Delay Ratio & Edge Weighting",
             [
                 ("Formula", "DelayRatio(e) = Actual_Travel_Time(e) / OSRM_Estimated_Time(e)"),
                 ("Corridor Weight", "W(u, v) = Median({ DelayRatio_i(u, v) | i in Trips(u, v) })"),
                 ("Why Median?", "Median resists extreme outliers (accidents/breakdowns) far better than arithmetic mean."),
                 ("Stratified", "Computed separately for FTL and Carting across Morning, Afternoon, Evening, Night.")
             ])

    add_card(s4, Inches(6.8), Inches(1.6), Inches(5.7), Inches(2.6),
             "2. Betweenness Centrality (Chokepoint Identification)",
             [
                 ("Formula", "C_B(v) = SUM_{s != v != t} [ sigma_st(v) / sigma_st ]"),
                 ("sigma_st", "Total number of shortest paths from node s to node t."),
                 ("sigma_st(v)", "Number of those shortest paths that pass through hub v."),
                 ("Physical Meaning", "Hubs with high C_B are inescapable bottlenecks. Gurgaon has C_B = 0.214 (21.4% of national routes pass through it).")
             ])

    add_card(s4, Inches(0.8), Inches(4.4), Inches(5.7), Inches(2.6),
             "3. GraphSAGE Inductive Neighborhood Convolution",
             [
                 ("Aggregation", "h_{N(v)}^{(k)} = AGG_k({ h_u^{(k-1)},  forall u in N(v) })"),
                 ("Node Update", "h_v^{(k)} = sigma( W^{(k)} * [ h_v^{(k-1)} || h_{N(v)}^{(k)} ] )"),
                 ("Inductive Power", "Unlike transductive methods, GraphSAGE can compute embeddings for newly added logistics hubs without retraining the whole graph.")
             ])

    add_card(s4, Inches(6.8), Inches(4.4), Inches(5.7), Inches(2.6),
             "4. Evaluation Metric: Within-K% Prediction Accuracy",
             [
                 ("Formula", "Acc_K% = (1/N) * SUM_{i=1}^N  I( |y_hat_i - y_i| / y_i <= K/100 )"),
                 ("Business Meaning", "Logistics managers care whether an ETA is accurate within operational tolerance (within 15% or 25% of promised window)."),
                 ("SLA Breach Definition", "Breach occurs if Actual Time > 1.25 * Promised Time (or delay > 60 mins).")
             ])

    # -------------------------------------------------------------
    # SLIDE 5: System Architecture & End-to-End Pipeline
    # -------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "End-to-End System Architecture Pipeline")

    tb5 = s5.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.2))
    tf5 = tb5.text_frame
    tf5.word_wrap = True
    arch_steps = [
        ("Step 1: Ingestion & Spatial Preprocessing", "Parses 144k raw scans, aggregates discrete corridor legs, performs Indian facility geocoding, filters sensor anomalies."),
        ("Step 2: Directed Weighted Graph Construction", "Constructs G = (V, E) with 1,589 Hubs and 2,501 directed corridor edges. Edge weights represent median delay ratios stratified by route type and hour."),
        ("Step 3: Centrality & Bottleneck Identification", "Audits structural risk using Betweenness, In/Out Degrees, and PageRank to generate composite Chokepoint Risk Scores (0-100)."),
        ("Step 4: Inductive Representation Learning", "Generates 16-D Node2Vec random-walk embeddings and inductive GraphSAGE neighborhood feature tensors."),
        ("Step 5: Gradient Boosting & Deep GNN ETA Models", "Trains and evaluates LightGBM/CatBoost with graph augmentations and 2-layer GraphSAGE GNN on PyTorch Geometric."),
        ("Step 6: Route Decision & Strategic ROI Engine", "Implements FTL vs. Carting trade-off matrix, dynamic congestion-bypass shortest path, and ₹3.24 Cr hub upgrade ROI simulation.")
    ]
    for i, (hd, bd) in enumerate(arch_steps):
        p = tf5.paragraphs[0] if i == 0 else tf5.add_paragraph()
        p.text = f"{hd} — {bd}"
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_DARK
        p.space_after = Pt(11)

    # -------------------------------------------------------------
    # SLIDE 6: Network Topology & Directed Graph Construction (NEW)
    # -------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Network Topology: 1,589 Hubs & 2,501 Directed Corridors")

    fig3 = "reports/figures/fig3_network_topology_bottlenecks.png"
    if os.path.exists(fig3):
        s6.shapes.add_picture(fig3, Inches(0.8), Inches(1.7), width=Inches(6.2))

    add_card(s6, Inches(7.2), Inches(1.7), Inches(5.3), Inches(5.3),
             "Topological Network Properties",
             [
                 ("Graph Structure", "Directed multigraph collapsed to weighted digraph G = (V, E). Nodes = Facilities, Edges = Active transport corridors."),
                 ("Node Count |V|", "1,589 hubs across all Indian states and Union Territories."),
                 ("Edge Count |E|", "2,501 directed corridor connections."),
                 ("Asymmetric Corridors", "Direction matters: Delhi -> Jaipur has delay ratio 1.25, while Jaipur -> Delhi has 1.58 due to evening toll congestion."),
                 ("Hub Degree Distribution", "Follows a scale-free power law distribution. A tiny 3% of hubs handle over 40% of national connectivity."),
                 ("Giant Connected Component", "Over 94% of hubs belong to a single strongly connected component, enabling nationwide multi-hop parcel transit.")
             ])

    # -------------------------------------------------------------
    # SLIDE 7: Network Bottleneck Audit & Top 5 Facilities
    # -------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Network Bottleneck Audit: Top 5 National Chokepoints")

    fig2 = "reports/figures/fig2_top_chokepoints_sla_breaches.png"
    if os.path.exists(fig2):
        s7.shapes.add_picture(fig2, Inches(0.8), Inches(1.8), width=Inches(6.0))

    tb7 = s7.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.5), Inches(5.0))
    tf7 = tb7.text_frame
    tf7.word_wrap = True
    hubs_info = [
        ("1. Gurgaon Bilaspur (Haryana)", "Betweenness: 0.214 | Risk Score: 97.7/100 | 1,225 SLA breaches. Master national consolidation hub. 21.4% of all optimal national routes cross this one facility."),
        ("2. Bangalore Nelamangala (Karnataka)", "Betweenness: 0.114 | Risk Score: 69.2/100 | 962 SLA breaches. Key southern freight anchor; heavy evening peak delays."),
        ("3. Bhiwandi Mankoli (Maharashtra)", "Risk Score: 59.4/100 | 965 SLA breaches. Western gateway handling immense e-commerce volume; high dock dwell."),
        ("4. Hyderabad Shamshabad (Telangana)", "Betweenness: 0.083 | Risk Score: 46.8/100 | 530 SLA breaches. Major south-central corridor bridge."),
        ("5. Kolkata Dankuni (West Bengal)", "Betweenness: 0.095 | Risk Score: 44.5/100 | 367 SLA breaches. Gateway connecting Northeast India to mainland.")
    ]
    for i, (h, b) in enumerate(hubs_info):
        p = tf7.paragraphs[0] if i == 0 else tf7.add_paragraph()
        p.text = f"• {h}\n  {b}"
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_DARK
        p.space_after = Pt(8)

    # -------------------------------------------------------------
    # SLIDE 8: Representation Learning (Node2Vec & GraphSAGE) (NEW)
    # -------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Representation Learning: Node2Vec & Deep GraphSAGE GNN")

    add_card(s8, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.3),
             "Node2Vec Random-Walk Embeddings",
             [
                 ("Concept", "Learns continuous 16-dimensional vector representations for each logistics hub by simulating biased second-order random walks."),
                 ("Biased Sampling Parameters", "p = 1.0 (return parameter), q = 0.5 (in-out parameter). Balances local community clustering (BFS) with global structural roles (DFS)."),
                 ("Walk Architecture", "Walk length = 10 hops, 10 walks per node, trained via Skip-Gram with negative sampling."),
                 ("Output Artifact", "data/node2vec_embeddings.pkl (16 dimensions per node)."),
                 ("Advantage", "Embeds geographical connectivity and routing hierarchy into dense numerical vectors fed directly into Gradient Boosting trees.")
             ])

    add_card(s8, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3),
             "PyTorch Geometric Deep GraphSAGE",
             [
                 ("Model Architecture", "2-Layer Graph Convolution Network built on torch_geometric.nn.SAGEConv."),
                 ("Layer 1", "SAGEConv(in_channels=8, out_channels=32) + ReLU + Dropout(0.2)."),
                 ("Layer 2", "SAGEConv(in_channels=32, out_channels=16) + Linear Readout -> ETA."),
                 ("Inductive Aggregation", "Mean-pooling across multi-hop incident corridors."),
                 ("Supervised Objective", "Trained end-to-end to minimize Mean Squared Error against actual segment transit times."),
                 ("Performance", "Achieves 36.0 min MAE on unseen test segments, confirming deep neighborhood convolutions capture physical delay waves.")
             ])

    # -------------------------------------------------------------
    # SLIDE 9: Benchmark Evaluation - The Graph Advantage Table
    # -------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Empirical Benchmarks: Measuring 'The Graph Advantage'")

    # Table of benchmark results
    t_shape9 = s9.shapes.add_table(6, 6, Inches(0.8), Inches(1.6), Inches(11.7), Inches(2.6))
    tbl9 = t_shape9.table

    b_headers = ["Model Architecture", "MAE (Hours)", "MAE (Mins)", "Within-15% Acc", "Within-25% Acc", "R² Score"]
    for col_idx, h in enumerate(b_headers):
        c = tbl9.cell(0, col_idx)
        c.text = h
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_BRAND
        for p in c.text_frame.paragraphs:
            p.font.bold = True
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_WHITE

    b_rows = [
        ["OSRM Routing Engine (Reference)", "1.489 h", "89.3 min", "7.06%", "13.80%", "0.726"],
        ["Baseline: Linear Regression", "0.766 h", "46.0 min", "27.90%", "42.92%", "0.935"],
        ["Baseline: Gradient Boosting (Trip-Level)", "0.711 h", "42.7 min", "30.27%", "46.98%", "0.944"],
        ["Graph: Deep GraphSAGE GNN (PyG)", "0.600 h", "36.0 min", "43.74%", "63.45%", "0.944"],
        ["Graph: Gradient Boosting (Best Model)", "0.511 h", "30.7 min", "48.67%", "67.45%", "0.961"]
    ]
    for r_idx, row in enumerate(b_rows, 1):
        for c_idx, val in enumerate(row):
            cell = tbl9.cell(r_idx, c_idx)
            cell.text = val
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(11)
                if r_idx == 5:
                    p.font.bold = True
                    p.font.color.rgb = COLOR_BRAND

    tb9 = s9.shapes.add_textbox(Inches(0.8), Inches(4.5), Inches(11.7), Inches(2.5))
    tf9 = tb9.text_frame
    tf9.word_wrap = True
    adv_points = [
        ("28.13% Error Reduction", "Adding graph topological features reduced Mean Absolute Error from 42.7 minutes (baseline) down to 30.7 minutes."),
        ("+18.40% Accuracy Gain", "Within-15% prediction accuracy jumped from 30.27% to 48.67%, representing a dramatic improvement in reliable delivery commitments."),
        ("OSRM Inadequacy", "OSRM alone is off by 89.3 minutes on average, with only 7.06% of predictions inside the 15% tolerance window.")
    ]
    for i, (hd, bd) in enumerate(adv_points):
        p = tf9.paragraphs[0] if i == 0 else tf9.add_paragraph()
        p.text = f"• {hd}: {bd}"
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_DARK
        p.space_after = Pt(8)

    # -------------------------------------------------------------
    # SLIDE 10: Benchmark Visuals & Feature Importance (NEW)
    # -------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Empirical Benchmark Visuals & Feature Importance")

    fig4 = "reports/figures/fig4_graph_advantage_benchmarks.png"
    if os.path.exists(fig4):
        s10.shapes.add_picture(fig4, Inches(0.8), Inches(1.6), width=Inches(7.2))

    add_card(s10, Inches(8.2), Inches(1.6), Inches(4.3), Inches(5.3),
             "Top Predictive Feature Weights",
             [
                 ("1. OSRM Travel Duration", "38.2% importance. Remains the core distance-time foundation."),
                 ("2. Corridor Median Delay Ratio", "21.4% importance. Captures chronic corridor congestion."),
                 ("3. Origin Hub Betweenness", "14.1% importance. Quantifies origin facility bottleneck probability."),
                 ("4. Node2Vec Walk Dimensions", "12.7% cumulative importance. Encodes structural multi-hop role."),
                 ("5. Route Type (FTL/Carting)", "8.3% importance. Reflects sorting dwell differences."),
                 ("Key Insight", "Graph features collectively account for >48% of total predictive power!")
             ])

    # -------------------------------------------------------------
    # SLIDE 11: Route-Type Decision Economics & Math (NEW)
    # -------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "Route Decision Economics: FTL vs. Carting Calculus")

    add_card(s11, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.3),
             "Cost & Dwell Mathematical Formulation",
             [
                 ("FTL Cost Model", "Cost_FTL(d) = C_FTL * d = INR 38/km * d"),
                 ("Carting Cost Model", "Cost_Carting(d, h) = C_Carting * d + H_dock * h = INR 22/km * d + INR 350 * h"),
                 ("Parameters", "C_FTL = INR 38/km | C_Carting = INR 22/km | H_dock = INR 350 per cross-dock sort."),
                 ("Breakeven Distance Formula", "D* = (H_dock * h) / (C_FTL - C_Carting) = (350 * h) / (38 - 22) = 21.875 * h km"),
                 ("Economic Trade-off", "Carting saves INR 16/km in transit fuel/lease, but incurs INR 350 in dock sorting fees plus 1.8 to 4.5 hours in transfer dwell.")
             ])

    add_card(s11, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3),
             "Automated Decision Rules Matrix",
             [
                 ("Rule 1: Long Haul (>300 km)", "Mandate FTL. Carting consolidation adds 3.5-5.2 hours in intermediate sorting dwell, triggering a 91% SLA breach rate on long corridors."),
                 ("Rule 2: Chokepoint Origin Hubs", "When dispatching from Gurgaon, Bangalore, or Bhiwandi, assign FTL to bypass overloaded sorting queues."),
                 ("Rule 3: Short Feeder Corridors (<100 km)", "Select Carting Consolidation. Yields INR 500 - INR 800 savings per consignment with minimal SLA breach risk (<4%)."),
                 ("Rule 4: High Parcel Value / Express SLA", "Assign FTL regardless of distance if parcel SLA tolerance is under 6 hours.")
             ])

    # -------------------------------------------------------------
    # SLIDE 12: FTL vs. Carting Trade-off Visual Outputs
    # -------------------------------------------------------------
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "Empirical Validation: FTL vs. Carting Performance")

    fig5 = "reports/figures/fig5_ftl_vs_carting_tradeoff.png"
    if os.path.exists(fig5):
        s12.shapes.add_picture(fig5, Inches(0.8), Inches(1.8), width=Inches(6.2))

    tb12 = s12.shapes.add_textbox(Inches(7.2), Inches(1.8), Inches(5.3), Inches(5.0))
    tf12 = tb12.text_frame
    tf12.word_wrap = True
    f_rules = [
        ("Median Delay Comparison", "FTL shipments experience a median delay ratio of 1.42x, whereas Carting shipments experience 2.18x (over 53% more delay)."),
        ("Dwell Overhead", "Carting vehicles spend an average of 142 minutes waiting at cross-dock loading bays compared to 28 minutes for FTL point-to-point."),
        ("SLA Breach Differential", "On corridors connecting Tier-1 hubs, Carting produces 4.8x more SLA breaches than FTL."),
        ("Operational Guideline", "Use Carting strictly for local feeder distribution; protect core trunkline corridors with scheduled FTL.")
    ]
    for i, (r_head, r_body) in enumerate(f_rules):
        p = tf12.paragraphs[0] if i == 0 else tf12.add_paragraph()
        p.text = f"• {r_head}: {r_body}"
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_DARK
        p.space_after = Pt(12)

    # -------------------------------------------------------------
    # SLIDE 13: Operations Strategy Memo & Capital ROI Calculus (NEW)
    # -------------------------------------------------------------
    s13 = prs.slides.add_slide(blank_layout)
    add_header(s13, "Operations Strategy Memo: Hub Upgrade ROI Simulation")

    add_card(s13, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.3),
             "Capital Allocation ROI Mathematical Model",
             [
                 ("Targeted Intervention", "Deploy automated cross-belt sorters and dynamic dock scheduling at the Top 3 Hubs: Gurgaon, Bangalore, Bhiwandi."),
                 ("Volume Concentration", "These 3 facilities process 15.6% of total national volume and touch 32.4% of all delayed consignments."),
                 ("Dwell Reduction Target", "Simulate a 40% reduction in dock dwell time through automated sorting."),
                 ("Late Delivery Reduction", "Delta_P_late = 7.01% network-wide reduction in total late deliveries."),
                 ("Financial Impact Formula", "Revenue_Recovered = Total_Late_Shipments * Delta_P_late * Avg_Consignment_Penalty"),
                 ("Net Annualized Benefit", "INR 32,406,400 (INR 3.24 Crores) in recovered revenue-at-risk!")
             ])

    add_card(s13, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3),
             "Implementation Roadmap & Phasing",
             [
                 ("Phase 1: Quick Wins (Months 1-3)", "Implement dynamic FTL/Carting dispatch rules and predictive ETA alerts in Delhivery TMS."),
                 ("Phase 2: Pilot Hub Modernization (Months 4-6)", "Automate cross-docking at Gurgaon Bilaspur facility; evaluate dwell reduction."),
                 ("Phase 3: National Rollout (Months 7-12)", "Scale automated sorting to Bangalore Nelamangala and Bhiwandi Mankoli; deploy dynamic bypass routing.")
             ])

    # -------------------------------------------------------------
    # SLIDE 14: Dynamic Bypass Routing Algorithm (NEW)
    # -------------------------------------------------------------
    s14 = prs.slides.add_slide(blank_layout)
    add_header(s14, "Dynamic Congestion-Bypass Routing Engine")

    add_card(s14, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.3),
             "Cost-Weighted Shortest Path Optimization",
             [
                 ("Objective Function", "Find path P* minimizing: Cost(P) = SUM_{e in P} [ T_OSRM(e) * W_delay(e) ] + SUM_{v in P} Penalty(v)"),
                 ("Chokepoint Penalty", "Penalty(v) = alpha * Chokepoint_Risk_Score(v)"),
                 ("Algorithm", "Congestion-weighted Dijkstra / A* with real-time incident edge penalties."),
                 ("Bypass Mechanism", "When Gurgaon Bilaspur exhibits severe backlog, the router dynamically diverts non-urgent cargo through satellite feeder hubs (e.g., Faridabad or Jaipur)."),
                 ("Results", "Saves 45-80 minutes per long-haul trip during evening congestion windows.")
             ])

    add_card(s14, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3),
             "Sample Bypass Output",
             [
                 ("Origin -> Destination", "IND122001AAA (Gurgaon) -> IND560001AAA (Bangalore)"),
                 ("Standard Route (Bottleneck)", "Via Bilaspur Master Hub: Expected transit 38.4 hours, SLA risk: HIGH (84%)."),
                 ("Optimized Bypass Route", "Via Satellite Feeder -> Direct FTL: Expected transit 33.1 hours, SLA risk: LOW (18%)."),
                 ("Time Saved", "5.3 hours avoided sorting queue dwell!"),
                 ("Cost Delta", "+INR 420 fuel cost offset by INR 2,500 avoided breach penalty.")
             ])

    # -------------------------------------------------------------
    # SLIDE 15: Watchtower Operations Dashboard & Production API
    # -------------------------------------------------------------
    s15 = prs.slides.add_slide(blank_layout)
    add_header(s15, "Production Delivery: Watchtower HUD & Flask REST API")

    tb15 = s15.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.2))
    tf15 = tb15.text_frame
    tf15.word_wrap = True
    prod_items = [
        ("1. Watchtower Operations HUD (Port 8501)", "High-contrast dark Cyberpunk operations theme with live system status, telemetry waveforms, national chokepoint monitor, interactive Leaflet routing map, and 1-click PDF export."),
        ("2. Real-Time REST API (Port 8000)", "Production Flask 3.1 service providing 6 high-throughput endpoints: /api/v1/predict/eta, /api/v1/hubs, /api/v1/corridors/bottlenecks, /api/v1/recommend/route-type, and /api/v1/route/optimize."),
        ("3. Sub-50ms Inference Latency", "Model pipeline serves real-time ETA predictions with confidence intervals and delay risk badges in <45ms."),
        ("4. Automated 1-Click Master Report Export", "Direct PDF report generation with ReportLab, embedded figures, and technical appendices available at /download/report.")
    ]
    for i, (hd, bd) in enumerate(prod_items):
        p = tf15.paragraphs[0] if i == 0 else tf15.add_paragraph()
        p.text = f"• {hd}\n  {bd}"
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_DARK
        p.space_after = Pt(12)

    # -------------------------------------------------------------
    # SLIDE 16: Faculty Viva Defense Q&A & Technical Takeaways
    # -------------------------------------------------------------
    s16 = prs.slides.add_slide(blank_layout)
    add_header(s16, "Faculty Viva Defense Summary & Core Takeaways")

    add_card(s16, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.3),
             "Top Viva Defense Questions & Answers",
             [
                 ("Q: Why not just use OSRM or Google Maps?", "A: Routing engines predict free-flow travel. They are blind to sorting dock dwell, vehicle turnarounds, and network chokepoints."),
                 ("Q: What is the core 'Graph Advantage'?", "A: Logistics is inherently relational. Adding betweenness centrality and Node2Vec embeddings cuts prediction error by 28.1% and boosts 15% accuracy by +18.4% points."),
                 ("Q: How was data leakage prevented?", "A: Strict temporal split (older trips train, newer trips test) + edge weights computed exclusively from training data.")
             ])

    add_card(s16, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3),
             "Project Accomplishments",
             [
                 ("1. Real Data Ingestion", "Engineered 144k+ Delhivery logistics scans into 26k+ corridor legs."),
                 ("2. Rigorous Modeling", "Benchmarked OSRM vs Baseline vs GraphSAGE GNN vs Graph-Enhanced Gradient Boosting."),
                 ("3. Quantifiable ROI", "Demonstrated INR 3.24 Crores in revenue-at-risk recovered through 3 hub upgrades."),
                 ("4. Production Ready", "Full REST API, Watchtower HUD, reproducible codebase, and GitHub repository.")
             ])

    prs.save(output_path)
    print(f"PowerPoint presentation successfully generated at {output_path} with {len(prs.slides)} slides!")


if __name__ == "__main__":
    build_powerpoint_deck()
