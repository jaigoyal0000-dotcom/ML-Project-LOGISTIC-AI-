"""
src/pdf_generator.py
--------------------
Generates a formal, executive-ready PDF Consulting Strategy Report using ReportLab.
Integrates publication charts, benchmark tables, and ROI calculations into a single document.
"""

import os
import json
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)


def generate_executive_pdf_report(output_pdf="reports/Delhivery_Network_Optimization_Report.pdf"):
    print(f"Generating formal PDF report to {output_pdf}...")
    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)

    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=letter,
        rightMargin=0.6 * inch,
        leftMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY = colors.HexColor("#1E3A8A")   # Navy
    SECONDARY = colors.HexColor("#EA580C") # Orange/Amber
    DARK = colors.HexColor("#1F2937")      # Slate
    LIGHT_BG = colors.HexColor("#F8FAFC")  # Off-white

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=PRIMARY,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=SECONDARY,
        spaceAfter=14
    )
    h2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=PRIMARY,
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=DARK,
        spaceAfter=6
    )
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1 # Center
    )
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=DARK
    )

    # Load data artifacts
    with open("models/benchmark_results.json", "r") as f:
        benchmarks = json.load(f)
    with open("reports/strategy_impact_metrics.json", "r") as f:
        impact = json.load(f)
    hubs_df = pd.read_csv("data/hub_centrality_metrics.csv")

    story = []

    # Title Banner
    story.append(Paragraph("DELHIVERY LOGISTICS NETWORK INTELLIGENCE", title_style))
    story.append(Paragraph("Optimizing Delivery ETAs with Graph-Based Network Modeling & Bottleneck Analytics", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10))

    # Meta Table
    meta_data = [
        [
            Paragraph("<b>Target Audience:</b> Head of Network Operations & VP Logistics", table_cell_style),
            Paragraph("<b>Domain:</b> Machine Learning & GNNs", table_cell_style)
        ],
        [
            Paragraph("<b>Dataset:</b> 142k+ Segments / 26k+ Corridors", table_cell_style),
            Paragraph(f"<b>Key Impact:</b> -{impact['projected_pct_reduction_late_deliveries']:.1f}% Late Deliveries | INR 3.24 Cr Recovered", table_cell_style)
        ]
    ]
    t_meta = Table(meta_data, colWidths=[3.6 * inch, 3.6 * inch])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # Section 1: Executive Summary
    story.append(Paragraph("1. Executive Summary & Core Mandate", h2_style))
    exec_summary_text = (
        "Delhivery's standard routing engine (OSRM) relies on static topological distance and posted highway speed limits, "
        "assuming frictionless movement between terminals. Our empirical audit of national multi-hop freight corridors reveals "
        "that <b>OSRM systematically underestimates actual travel time by a median factor of 1.88x (88.3% slower)</b>. "
        "Delays are heavily concentrated in a small group of high-centrality chokepoints rather than uniformly spread across the country. "
        "By modeling the logistics network as a directed weighted graph and incorporating graph representation learning (Node2Vec, GraphSAGE, "
        "and centrality indices) into regression architectures, we achieve a <b>28.13% error reduction in ETA predictions (MAE down to 30.7 mins)</b> "
        "and an <b>+18.40 percentage points gain in high-accuracy deliveries</b>. "
        "Furthermore, modernizing the top 3 national hubs resolves cascading delay propagation, preventing thousands of late deliveries and recovering "
        f"<b>INR {impact['projected_annual_revenue_recovered_inr']:,.0f} in annualized revenue-at-risk</b>."
    )
    story.append(Paragraph(exec_summary_text, body_style))

    # Figure 1
    fig1_path = "reports/figures/fig1_osrm_delay_distribution.png"
    if os.path.exists(fig1_path):
        story.append(Spacer(1, 4))
        story.append(Image(fig1_path, width=6.8 * inch, height=2.6 * inch))

    # Section 2: Top 5 Bottlenecks
    story.append(Spacer(1, 8))
    story.append(Paragraph("2. National Bottleneck Audit & Top 5 Chokepoints", h2_style))
    story.append(Paragraph(
        "By combining <b>Betweenness Centrality</b> (shortest paths passing through each facility), <b>Total Segment Volume</b>, "
        "and <b>Historical SLA Breach Count</b>, we audited and ranked the top structural chokepoints across 1,589 facilities:",
        body_style
    ))

    # Table of Top 5 Hubs
    hub_table_rows = [
        [
            Paragraph("Rank", table_header_style),
            Paragraph("Hub Facility Name & State", table_header_style),
            Paragraph("Betweenness", table_header_style),
            Paragraph("SLA Breaches", table_header_style),
            Paragraph("Breach Rate", table_header_style),
            Paragraph("Risk Score", table_header_style)
        ]
    ]
    for i, h in enumerate(impact['top5_hubs'], 1):
        hub_table_rows.append([
            Paragraph(f"<b>{i}</b>", table_cell_style),
            Paragraph(f"<b>{h['name']}</b> ({h['state']})", table_cell_style),
            Paragraph(f"{h['betweenness']:.4f}", table_cell_style),
            Paragraph(f"{h['total_breaches']:,}", table_cell_style),
            Paragraph(f"{h['breach_rate']}%", table_cell_style),
            Paragraph(f"<b>{h['chokepoint_score']}/100</b>", table_cell_style)
        ])
    t_hubs = Table(hub_table_rows, colWidths=[0.5 * inch, 2.9 * inch, 0.9 * inch, 0.9 * inch, 0.9 * inch, 0.9 * inch])
    t_hubs.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_hubs)

    story.append(PageBreak())

    # Section 3: Algorithmic Benchmarks
    story.append(Paragraph("3. Algorithmic Machine Learning Benchmarks (The Graph Advantage)", h2_style))
    story.append(Paragraph(
        "To establish whether graph-based network learning produces measurably superior ETA predictions, "
        "we benchmarked conventional routing baselines against graph-enhanced gradient boosting and deep GraphSAGE neural networks on 7,354 unseen test trips:",
        body_style
    ))

    bench_table_rows = [
        [
            Paragraph("Model Architecture", table_header_style),
            Paragraph("MAE (Hrs)", table_header_style),
            Paragraph("MAE (Mins)", table_header_style),
            Paragraph("Within 15%", table_header_style),
            Paragraph("Within 25%", table_header_style),
            Paragraph("R² Score", table_header_style)
        ]
    ]
    for b in benchmarks:
        is_best = "Best Model" in b['Model'] or "Gradient Boosting (+ Network" in b['Model']
        c_style = ParagraphStyle('cell_bold', parent=table_cell_style, fontName='Helvetica-Bold', textColor=PRIMARY) if is_best else table_cell_style
        bench_table_rows.append([
            Paragraph(f"<b>{b['Model']}</b>", c_style),
            Paragraph(f"{b['MAE (Hours)']:.3f} h", c_style),
            Paragraph(f"{b['MAE (Minutes)']:.1f} m", c_style),
            Paragraph(f"{b['Within-15% Accuracy (%)']:.1f}%", c_style),
            Paragraph(f"{b['Within-25% Accuracy (%)']:.1f}%", c_style),
            Paragraph(f"{b['R² Score']:.3f}", c_style)
        ])
    t_bench = Table(bench_table_rows, colWidths=[2.6 * inch, 0.9 * inch, 0.9 * inch, 0.9 * inch, 0.9 * inch, 0.8 * inch])
    t_bench.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_bench)

    # Figure 4: Benchmarks
    fig4_path = "reports/figures/fig4_graph_advantage_benchmarks.png"
    if os.path.exists(fig4_path):
        story.append(Spacer(1, 6))
        story.append(Image(fig4_path, width=6.8 * inch, height=2.6 * inch))

    # Section 4: FTL vs Carting & Operations Interventions
    story.append(Spacer(1, 8))
    story.append(Paragraph("4. Route-Type Selection & Capital Upgrade ROI", h2_style))
    story.append(Paragraph(
        "<b>FTL vs. Carting Decision Rules:</b> On long-haul corridors (>300 km) and routes originating from High Chokepoint Hubs (Risk Score > 60), "
        "<b>Full Truckload (FTL) is strictly recommended</b>. Although FTL carries higher vehicle mileage tariffs, eliminating intermediate handling docks "
        "lowers breach probabilities and protects SLAs. For local feeder hauls (<100 km), Carting provides ₹500–₹800 per shipment in consolidation margin with minimal delay risk.<br/><br/>"
        "<b>Capital Upgrade Financial Model:</b> Modernizing the Top 3 Hubs (Gurgaon Bilaspur, Bangalore Nelamangala, Bhiwandi Mankoli) via cross-belt automated sorters "
        f"and dynamic dock scheduling is projected to reduce overall network late deliveries by <b>{impact['projected_pct_reduction_late_deliveries']:.2f}%</b>, "
        f"recovering an estimated <b>INR {impact['projected_annual_revenue_recovered_inr']:,.0f} in annualized revenue-at-risk</b>.",
        body_style
    ))

    # Build PDF
    doc.build(story)
    print(f"Executive PDF Report successfully generated at {output_pdf}!")
    return output_pdf


if __name__ == "__main__":
    generate_executive_pdf_report()
