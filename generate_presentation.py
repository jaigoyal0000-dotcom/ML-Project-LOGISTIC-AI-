"""
generate_presentation.py
------------------------
Generates a 10-slide PowerPoint presentation deck (presentation_slides.pptx)
ready for tomorrow's faculty evaluation and technical viva defense.
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
    print(f"Creating PowerPoint presentation at {output_path}...")
    prs = Presentation()
    prs.slide_width = Inches(13.333) # 16:9 widescreen
    prs.slide_height = Inches(7.5)

    # Theme Colors
    COLOR_PRIMARY = RGBColor(30, 58, 138)    # Deep Navy
    COLOR_SECONDARY = RGBColor(234, 88, 12)  # Amber / Orange
    COLOR_DARK = RGBColor(31, 41, 55)        # Charcoal
    COLOR_LIGHT = RGBColor(248, 250, 252)    # Off-white
    COLOR_ACCENT = RGBColor(16, 185, 129)    # Emerald Green

    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title_text, category="DELHIVERY NETWORK INTELLIGENCE"):
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.1))
        tf = header_box.text_frame
        tf.word_wrap = True
        
        p_cat = tf.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_SECONDARY
        
        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_PRIMARY

    # -------------------------------------------------------------
    # SLIDE 1: Title Slide
    # -------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = COLOR_PRIMARY
    bg1.line.fill.background()

    t_box = s1.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.3), Inches(3.2))
    tf1 = t_box.text_frame
    p1 = tf1.paragraphs[0]
    p1.text = "Optimizing Delivery ETAs with\nGraph-Based Network Intelligence"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(255, 255, 255)

    p1_sub = tf1.add_paragraph()
    p1_sub.text = "Predictive Logistics Analytics · Graph Neural Networks · Delhivery Freight Network"
    p1_sub.font.size = Pt(18)
    p1_sub.font.color.rgb = RGBColor(209, 213, 219)
    p1_sub.space_before = Pt(15)

    p1_auth = tf1.add_paragraph()
    p1_auth.text = "Machine Learning Project Presentation & Technical Viva Defense"
    p1_auth.font.size = Pt(14)
    p1_auth.font.color.rgb = COLOR_SECONDARY
    p1_auth.space_before = Pt(30)

    # -------------------------------------------------------------
    # SLIDE 2: Industry Context & The Problem
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "The Real-World Challenge: Why OSRM Fails in Freight Logistics")

    tb2 = s2.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(6.0), Inches(5.2))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    bullets2 = [
        ("The Industry Context:", "Delhivery is India's largest integrated logistics provider, transporting millions of parcels through multi-hop hub-and-spoke routes."),
        ("Routing Engine Shortcoming:", "Delhivery uses OSRM (Open Source Routing Machine), which assumes free-flow traffic and shortest geometric paths."),
        ("The Empirical Reality:", "Our audit of 142,000+ segment scans revealed that OSRM underestimates actual travel times by a median factor of 1.88x (88% slower)."),
        ("Cascading Network Delays:", "Delays are not random: sorting bottlenecks, dock dwell times, and vehicle queues at major chokepoint hubs ripple throughout downstream deliveries."),
        ("Business Impact:", "Missed delivery promises, SLA penalties, customer churn, and disrupted linehaul scheduling.")
    ]
    for i, (title, desc) in enumerate(bullets2):
        p = tf2.paragraphs[0] if i == 0 else tf2.add_paragraph()
        p.text = f"• {title} {desc}"
        p.font.size = Pt(14)
        p.font.color.rgb = COLOR_DARK
        p.space_after = Pt(12)

    # Add Figure 1 image if available
    fig1 = "reports/figures/fig1_osrm_delay_distribution.png"
    if os.path.exists(fig1):
        s2.shapes.add_picture(fig1, Inches(7.0), Inches(1.8), width=Inches(5.5))

    # -------------------------------------------------------------
    # SLIDE 3: Proposed Graph Solution & Architecture
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "System Architecture: End-to-End Network Intelligence")

    tb3 = s3.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.0))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    steps = [
        ("1. Data Pipeline & Leakage Prevention:", "Parsed and merged 142k+ raw scans into 26,214 discrete corridor legs. Strictly isolated training and testing splits to avoid target leakage."),
        ("2. Directed Weighted Network Graph:", "1,589 Hubs (Nodes) and 2,501 Corridors (Edges). Weights capture median actual-vs-OSRM delay ratios stratified by route type and time of day."),
        ("3. Structural Centrality & Chokepoint Audit:", "Computed Betweenness Centrality, In/Out Degrees, and Clustering Coefficients to identify systemic single-points-of-failure."),
        ("4. Graph Representation Learning:", "Trained 16-dimensional Node2Vec random-walk embeddings and inductive GraphSAGE neighborhood aggregations."),
        ("5. Dual ML Pipeline & Benchmarking:", "Benchmarked Trip-Level Baseline Regression vs. Graph-Enhanced Random Forest, Gradient Boosting, and PyTorch Geometric GNN."),
        ("6. Decision Support & Strategy Memo:", "Built automated FTL vs. Carting decision framework, hub upgrade ROI model, and interactive Streamlit web dashboard.")
    ]
    for i, (head, body) in enumerate(steps):
        p = tf3.paragraphs[0] if i == 0 else tf3.add_paragraph()
        p.text = f"{head} {body}"
        p.font.size = Pt(14)
        p.font.color.rgb = COLOR_DARK
        p.space_after = Pt(10)

    # -------------------------------------------------------------
    # SLIDE 4: Network Topology & Bottleneck Audit
    # -------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Network Bottleneck Audit: Top 5 National Chokepoints")

    # Add Figure 2 if available
    fig2 = "reports/figures/fig2_top_chokepoints_sla_breaches.png"
    if os.path.exists(fig2):
        s4.shapes.add_picture(fig2, Inches(0.8), Inches(1.8), width=Inches(6.0))

    tb4 = s4.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.5), Inches(5.0))
    tf4 = tb4.text_frame
    tf4.word_wrap = True
    hubs_info = [
        ("1. Gurgaon Bilaspur (Haryana):", "Betweenness = 0.214 | 1,225 SLA breaches. Master national consolidation hub; over 21% of all optimal national routes cross this facility."),
        ("2. Bangalore Nelamangala (Karnataka):", "Betweenness = 0.114 | 962 SLA breaches. Southern freight anchor; heavy evening peak delays."),
        ("3. Bhiwandi Mankoli (Maharashtra):", "965 SLA breaches. Western gateway handling immense e-commerce volume; high dock dwell."),
        ("4. Hyderabad Shamshabad (Telangana):", "Betweenness = 0.083 | 530 SLA breaches. Regional chokepoint connecting South-Central corridors."),
        ("5. Kolkata Dankuni (West Bengal):", "Betweenness = 0.095 | 367 SLA breaches. Eastern corridor gateway connecting NE and East India.")
    ]
    for i, (h, b) in enumerate(hubs_info):
        p = tf4.paragraphs[0] if i == 0 else tf4.add_paragraph()
        p.text = f"{h}\n{b}"
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_DARK
        p.space_after = Pt(8)

    # -------------------------------------------------------------
    # SLIDE 5: Model Evaluation - The Graph Advantage
    # -------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Empirical Benchmarks: Measuring 'The Graph Advantage'")

    # Table of benchmark results
    table_shape = s5.shapes.add_table(6, 6, Inches(0.8), Inches(1.6), Inches(11.7), Inches(2.4))
    table = table_shape.table

    headers = ["Model Architecture", "MAE (Hours)", "MAE (Mins)", "Within-15% Acc", "Within-25% Acc", "R² Score"]
    for col_idx, h in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_PRIMARY
        for p in cell.text_frame.paragraphs:
            p.font.bold = True
            p.font.size = Pt(12)
            p.font.color.rgb = RGBColor(255, 255, 255)

    rows_data = [
        ["OSRM Routing Engine (Ref)", "1.489 h", "89.3 min", "7.06%", "13.80%", "0.726"],
        ["Baseline: Linear Regression", "0.766 h", "46.0 min", "27.90%", "42.92%", "0.935"],
        ["Baseline: Gradient Boosting (Trip-Level)", "0.711 h", "42.7 min", "30.27%", "46.98%", "0.944"],
        ["Graph: Deep GraphSAGE GNN (PyG)", "0.600 h", "36.0 min", "43.74%", "63.45%", "0.944"],
        ["Graph: Gradient Boosting (Best Model)", "0.511 h", "30.7 min", "48.67%", "67.45%", "0.961"]
    ]
    for r_idx, row in enumerate(rows_data, 1):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.text = val
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(11)
                if r_idx == 5:
                    p.font.bold = True
                    p.font.color.rgb = COLOR_PRIMARY

    tb5 = s5.shapes.add_textbox(Inches(0.8), Inches(4.3), Inches(11.7), Inches(2.6))
    tf5 = tb5.text_frame
    tf5.word_wrap = True
    adv_points = [
        "KEY TAKEAWAYS ON 'THE GRAPH ADVANTAGE':",
        "• Error Reduction: Graph features reduced Mean Absolute Error by 28.13% (from 42.7 minutes down to 30.7 minutes).",
        "• High-Accuracy Predictions: The proportion of trips predicted within ±15% of actual arrival surged from 30.27% to 48.67% (+18.40 percentage points).",
        "• Deep GNN Validation: PyTorch Geometric GraphSAGE achieved 36.0 min MAE and 43.74% accuracy, confirming that inductive neighborhood aggregation reliably captures network topology."
    ]
    for i, pt in enumerate(adv_points):
        p = tf5.paragraphs[0] if i == 0 else tf5.add_paragraph()
        p.text = pt
        p.font.size = Pt(13) if i == 0 else Pt(12)
        p.font.bold = True if i == 0 else False
        p.font.color.rgb = COLOR_SECONDARY if i == 0 else COLOR_DARK
        p.space_after = Pt(6)

    # -------------------------------------------------------------
    # SLIDE 6: Feature Importance Analysis
    # -------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Feature Importance: What Drives Real-World Travel Times?")

    fig4 = "reports/figures/fig4_graph_advantage_benchmarks.png"
    if os.path.exists(fig4):
        s6.shapes.add_picture(fig4, Inches(0.8), Inches(1.8), width=Inches(11.7))

    # -------------------------------------------------------------
    # SLIDE 7: FTL vs. Carting Decision Framework
    # -------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Route-Type Decision Framework: FTL vs. Carting")

    fig5 = "reports/figures/fig5_ftl_vs_carting_tradeoff.png"
    if os.path.exists(fig5):
        s7.shapes.add_picture(fig5, Inches(0.8), Inches(1.8), width=Inches(6.2))

    tb7 = s7.shapes.add_textbox(Inches(7.2), Inches(1.8), Inches(5.3), Inches(5.0))
    tf7 = tb7.text_frame
    tf7.word_wrap = True
    f_rules = [
        ("Trade-Off Quantified:", "FTL costs more per km (₹38 vs ₹22) but bypasses sorting docks. Carting carries a ₹350 dwell handling overhead per hop."),
        ("Rule 1 (Long Corridors >300 km):", "Mandate Dedicated FTL. Carting adds 3.5 to 5.2 hours in sorting dwell, triggering a 91% SLA breach rate."),
        ("Rule 2 (High Chokepoint Origin):", "When originating from facilities like Gurgaon or Bangalore, FTL protects delivery promises by skipping bottleneck queues."),
        ("Rule 3 (Short Feeder Runs <100 km):", "Select Carting Consolidation. Captures ₹500 to ₹800 in freight savings with minimal SLA divergence.")
    ]
    for i, (r_head, r_body) in enumerate(f_rules):
        p = tf7.paragraphs[0] if i == 0 else tf7.add_paragraph()
        p.text = f"{r_head} {r_body}"
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_DARK
        p.space_after = Pt(10)

    # -------------------------------------------------------------
    # SLIDE 8: Operations Strategy Memo & Capital Upgrade ROI
    # -------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Operations Strategy Memo: Hub Upgrade ROI Simulation")

    tb8 = s8.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf8 = tb8.text_frame
    tf8.word_wrap = True
    memo_bullets = [
        ("Consulting Recommendation for Delhivery Leadership:", "Upgrades should not be distributed evenly across 1,500+ facilities. Capital must be focused where structural risk and volume intersect."),
        ("Targeted Upgrade Intervention:", "Deploy automated cross-belt sorters and dynamic dock scheduling at the Top 3 Hubs: Gurgaon Bilaspur, Bangalore Nelamangala, and Bhiwandi Mankoli."),
        ("SLA Breach Concentration:", "These top 3 hubs touch over 15.6% of all network volume and account for a staggering share of national delay breaches."),
        ("Projected Delivery Improvement:", "A 40% reduction in dock dwell at these 3 facilities achieves a 7.01% network-wide reduction in total late deliveries."),
        ("Revenue-at-Risk Recovered:", "Prevents thousands of breached consignments, directly recovering an estimated ₹32,406,400 (₹3.24 Crores) in annualized revenue-at-risk.")
    ]
    for i, (m_h, m_b) in enumerate(memo_bullets):
        p = tf8.paragraphs[0] if i == 0 else tf8.add_paragraph()
        p.text = f"• {m_h} {m_b}"
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_DARK
        p.space_after = Pt(12)

    # -------------------------------------------------------------
    # SLIDE 9: Live Streamlit Application Demo
    # -------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Working Prototype: Interactive Decision Support Dashboard")

    tb9 = s9.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf9 = tb9.text_frame
    tf9.word_wrap = True
    dash_sections = [
        ("1. Executive Overview & KPIs:", "Live tracking of network delay distributions, chronic corridor ratios, and state volume concentrations."),
        ("2. Interactive Network Graph Visualizer:", "Filter corridors by delay ratio (>1.2x chronic delay) and route type with directed edge weights."),
        ("3. Chokepoint Hub Inspector:", "Deep-dive into incoming and outgoing incident corridors for any facility in India."),
        ("4. Smart ETA Predictor:", "Interactive calculator comparing OSRM vs. Baseline vs. Graph Model predictions with automated delay risk alerts."),
        ("5. FTL vs. Carting Simulator:", "Real-time economic and delivery time comparator for dispatchers."),
        ("6. Capital Upgrade ROI Simulator:", "Interactive sliders allowing leadership to simulate modernizing 1 to 5 hubs and viewing financial returns.")
    ]
    for i, (d_h, d_b) in enumerate(dash_sections):
        p = tf9.paragraphs[0] if i == 0 else tf9.add_paragraph()
        p.text = f"• {d_h} {d_b}"
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_DARK
        p.space_after = Pt(10)

    # -------------------------------------------------------------
    # SLIDE 10: Conclusion & Technical Viva Summary
    # -------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Summary & Technical Viva Defense Takeaways")

    tb10 = s10.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf10 = tb10.text_frame
    tf10.word_wrap = True
    viva_summary = [
        ("Core Takeaway:", "Logistics is inherently topological. Predicting travel time purely from individual shipment features leaves critical structural risks invisible."),
        ("Graph Contribution:", "Directed weighted network graphs, betweenness centrality, Node2Vec embeddings, and GraphSAGE neighborhood convolutions reduce MAE by 28.1% and boost 15% accuracy by +18.4% points."),
        ("Business Value:", "Delivered a data-backed FTL vs. Carting decision framework and demonstrated ₹3.24 Crores in revenue-at-risk recovered through prioritized hub upgrades."),
        ("Production Readiness:", "Fully reproducible Python pipeline, PyTorch Geometric implementation, and a live Streamlit dashboard ready for operational deployment.")
    ]
    for i, (v_h, v_b) in enumerate(viva_summary):
        p = tf10.paragraphs[0] if i == 0 else tf10.add_paragraph()
        p.text = f"✔ {v_h} {v_b}"
        p.font.size = Pt(14)
        p.font.color.rgb = COLOR_DARK
        p.space_after = Pt(14)

    prs.save(output_path)
    print(f"PowerPoint presentation successfully generated at {output_path}!")


if __name__ == "__main__":
    build_powerpoint_deck()

