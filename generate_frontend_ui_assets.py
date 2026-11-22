"""
generate_frontend_ui_assets.py
-------------------------------
Generates high-fidelity visual representations of each frontend dashboard view
in the Watchtower Operations HUD aesthetic (#0A0C10 / #11141D / #00FF66 / #00F0FF)
to embed into the Frontend PowerPoint Deck.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs("reports/figures", exist_ok=True)
plt.rcParams['font.family'] = 'sans-serif'


def render_watchtower_hud():
    """Renders the main Watchtower HUD view matching the user's uploaded reference."""
    fig = plt.figure(figsize=(14, 8), facecolor='#0A0C10')
    ax = fig.add_subplot(111)
    ax.set_facecolor('#0A0C10')
    ax.axis('off')

    # Top KPI Cards
    kpis = [
        ("ACTIVE HUBS", "1,589", "+12", "#00FF66", "CAP: 1,600 NODES"),
        ("SIGNAL QUALITY", "98.5%", "+0.5%", "#FACC15", "AVG_CHANNELS_OK"),
        ("ALERTS (24H)", "0", "NULL", "#E2E8F0", "SYSTEM_OPTIMAL"),
        ("SAFETY STATUS", "OPTIMAL", "STABLE", "#00FF66", "PARAMS: SAFE_RANGE")
    ]
    card_w, card_h = 0.22, 0.22
    for i, (title, val, badge, color, sub) in enumerate(kpis):
        x = 0.04 + i * 0.24
        y = 0.72
        # Card background
        rect = patches.FancyBboxPatch((x, y), card_w, card_h, boxstyle="round,pad=0.01,rounding_size=0.02",
                                      facecolor='#11141D', edgecolor='#1E293B', linewidth=1.5)
        ax.add_patch(rect)
        if i == 3:
            rect.set_edgecolor('#00FF66')
            rect.set_linewidth(2.0)
            
        ax.text(x + 0.02, y + 0.17, title, color='#94A3B8', fontsize=11, weight='bold')
        ax.text(x + 0.02, y + 0.07, val, color='#FFFFFF', fontsize=24, weight='bold')
        ax.text(x + 0.14, y + 0.07, f" {badge} ", color='#0A0C10', fontsize=10, weight='bold',
                bbox=dict(boxstyle='square,pad=0.2', facecolor=color, edgecolor='none'))
        ax.text(x + 0.02, y + 0.02, sub, color='#64748B', fontsize=9, weight='bold')

    # Stream 1 Waveform (Alpha / Transit Rhythm)
    s1_rect = patches.FancyBboxPatch((0.04, 0.38), 0.62, 0.30, boxstyle="round,pad=0.01,rounding_size=0.02",
                                    facecolor='#11141D', edgecolor='#1E293B', linewidth=1.5)
    ax.add_patch(s1_rect)
    ax.text(0.06, 0.63, "STREAM_01: CORRIDOR TRANSIT RHYTHM (ALPHA/BETA)", color='#FFFFFF', fontsize=12, weight='bold')
    ax.text(0.50, 0.63, "LIVE", color='#0A0C10', fontsize=9, weight='bold',
            bbox=dict(boxstyle='square,pad=0.2', facecolor='#00F0FF', edgecolor='none'))
    ax.text(0.55, 0.63, "STABLE", color='#00FF66', fontsize=10, weight='bold')

    # Draw cyan waveform
    t = np.linspace(0, 10, 300)
    wave1 = 0.5 + 0.08 * np.sin(3 * t) * np.exp(t/15) + 0.03 * np.sin(12 * t)
    x_coords = 0.06 + (t / 10) * 0.58
    y_coords = 0.40 + (wave1 - wave1.min()) / (wave1.max() - wave1.min()) * 0.20
    ax.plot(x_coords, y_coords, color='#00F0FF', linewidth=2.2)

    # Stream 2 Waveform (Gamma / Chokepoint Queues)
    s2_rect = patches.FancyBboxPatch((0.04, 0.04), 0.62, 0.30, boxstyle="round,pad=0.01,rounding_size=0.02",
                                    facecolor='#11141D', edgecolor='#1E293B', linewidth=1.5)
    ax.add_patch(s2_rect)
    ax.text(0.06, 0.29, "STREAM_02: CHOKEPOINT QUEUE ACTIVITY (GAMMA)", color='#FFFFFF', fontsize=12, weight='bold')
    ax.text(0.48, 0.29, "ELEVATED", color='#0A0C10', fontsize=9, weight='bold',
            bbox=dict(boxstyle='square,pad=0.2', facecolor='#FACC15', edgecolor='none'))
    ax.text(0.56, 0.29, "+52% OVER BASELINE", color='#FACC15', fontsize=10, weight='bold')

    # Draw yellow waveform
    wave2 = 0.5 + 0.09 * np.sin(8 * t) + 0.05 * np.cos(20 * t)
    y_coords2 = 0.06 + (wave2 - wave2.min()) / (wave2.max() - wave2.min()) * 0.20
    ax.plot(x_coords, y_coords2, color='#FACC15', linewidth=2.0)

    # Right Chokepoint Subject List Card
    sub_rect = patches.FancyBboxPatch((0.70, 0.04), 0.26, 0.64, boxstyle="round,pad=0.01,rounding_size=0.02",
                                     facecolor='#11141D', edgecolor='#1E293B', linewidth=1.5)
    ax.add_patch(sub_rect)
    ax.text(0.72, 0.63, "CHOKEPOINT HUBS", color='#FFFFFF', fontsize=13, weight='bold')
    ax.text(0.88, 0.63, "VIEW ALL", color='#00F0FF', fontsize=10, weight='bold')

    subjects = [
        ("SUB-001", "GURGAON BILASPUR", "REC", "97%", "#00FF66"),
        ("SUB-002", "BANGALORE NELAMANGALA", "REC", "88%", "#00FF66"),
        ("SUB-003", "BHIWANDI MANKOLI", "CALIB", "59%", "#FACC15"),
        ("SUB-004", "HYDERABAD SHAMSHABAD", "REC", "47%", "#00FF66"),
        ("SUB-005", "KOLKATA DANKUNI", "STBY", "44%", "#E2E8F0"),
        ("SUB-006", "AHMEDABAD ASLALI", "CRIT", "38%", "#FF3366")
    ]
    for idx, (sid, name, mode, pwr, dot_col) in enumerate(subjects):
        yy = 0.54 - idx * 0.09
        ax.plot([0.72], [yy + 0.015], marker='s', markersize=8, color=dot_col)
        ax.text(0.74, yy + 0.01, sid, color='#E2E8F0', fontsize=11, weight='bold')
        ax.text(0.74, yy - 0.02, name[:18], color='#64748B', fontsize=8, weight='bold')
        ax.text(0.85, yy + 0.01, f" {mode} ", color='#0A0C10', fontsize=8, weight='bold',
                bbox=dict(boxstyle='square,pad=0.2', facecolor='#E2E8F0', edgecolor='none'))
        ax.text(0.91, yy + 0.01, pwr, color='#E2E8F0', fontsize=11, weight='bold')

    plt.tight_layout()
    fig.savefig("reports/figures/ui_hud_overview.png", dpi=200, facecolor='#0A0C10')
    plt.close()
    print("Generated: reports/figures/ui_hud_overview.png")


def render_eta_predictor():
    """Renders the Smart ETA Predictor view."""
    fig = plt.figure(figsize=(14, 8), facecolor='#0A0C10')
    ax = fig.add_subplot(111)
    ax.set_facecolor('#0A0C10')
    ax.axis('off')

    # Header
    ax.text(0.04, 0.92, "SMART ETA PREDICTOR // GRAPH INFERENCE ENGINE", color='#00F0FF', fontsize=18, weight='bold')
    ax.text(0.04, 0.88, "Compares OSRM routing baseline vs. Graph-Enhanced Gradient Boosting in real time", color='#94A3B8', fontsize=12)

    # Input Parameters Panel
    in_rect = patches.FancyBboxPatch((0.04, 0.15), 0.35, 0.68, boxstyle="round,pad=0.01,rounding_size=0.02",
                                     facecolor='#11141D', edgecolor='#1E293B', linewidth=1.5)
    ax.add_patch(in_rect)
    ax.text(0.07, 0.78, "SHIPMENT PARAMETERS", color='#FFFFFF', fontsize=14, weight='bold')
    
    params = [
        ("ORIGIN HUB", "IND000000ACB (Gurgaon Bilaspur)"),
        ("DESTINATION HUB", "IND562132AAA (Bangalore Nelamangala)"),
        ("OSRM DISTANCE", "2,140.5 km"),
        ("OSRM ESTIMATED TIME", "34.2 hours"),
        ("ROUTE TYPE", "FTL (Full Truckload)"),
        ("DEPARTURE TIME", "18:00 (Evening Peak Window)")
    ]
    for i, (k, v) in enumerate(params):
        yy = 0.70 - i * 0.09
        ax.text(0.07, yy + 0.02, k, color='#64748B', fontsize=10, weight='bold')
        ax.text(0.07, yy - 0.01, v, color='#00FF66' if 'FTL' in v else '#FFFFFF', fontsize=12, weight='bold')

    # Output Comparison Cards
    models = [
        ("OSRM ENGINE BASELINE", "34.2h", "89.3 min error", "#64748B", "UNRELIABLE (7% within tolerance)"),
        ("BASELINE GRADIENT BOOSTING", "42.8h", "42.7 min error", "#FACC15", "MODERATE RISK (+8.6h queue)"),
        ("GRAPH-ENHANCED MODEL (BEST)", "39.5h", "30.7 min error", "#00FF66", "OPTIMAL (-28.1% ERROR REDUCTION)")
    ]
    for i, (m_name, pred, err, col, badge) in enumerate(models):
        x = 0.43
        y = 0.58 - i * 0.20
        c_rect = patches.FancyBboxPatch((x, y), 0.53, 0.17, boxstyle="round,pad=0.01,rounding_size=0.02",
                                        facecolor='#11141D', edgecolor=col, linewidth=2.0 if i==2 else 1.2)
        ax.add_patch(c_rect)
        ax.text(x + 0.03, y + 0.12, m_name, color=col, fontsize=12, weight='bold')
        ax.text(x + 0.03, y + 0.04, f"ETA: {pred}", color='#FFFFFF', fontsize=22, weight='bold')
        ax.text(x + 0.22, y + 0.05, f"MAE: {err}", color='#94A3B8', fontsize=12)
        ax.text(x + 0.35, y + 0.11, f" {badge} ", color='#0A0C10', fontsize=9, weight='bold',
                bbox=dict(boxstyle='square,pad=0.2', facecolor=col, edgecolor='none'))

    # Confidence Interval Gauge
    g_rect = patches.FancyBboxPatch((0.43, 0.15), 0.53, 0.16, boxstyle="round,pad=0.01,rounding_size=0.02",
                                    facecolor='#11141D', edgecolor='#00F0FF', linewidth=1.5)
    ax.add_patch(g_rect)
    ax.text(0.45, 0.26, "CONFIDENCE INTERVAL (90%)", color='#00F0FF', fontsize=11, weight='bold')
    ax.text(0.45, 0.18, "37.9h  ◄─────────── [ 39.5h ] ───────────►  41.1h", color='#FFFFFF', fontsize=15, weight='bold')

    plt.tight_layout()
    fig.savefig("reports/figures/ui_eta_predictor.png", dpi=200, facecolor='#0A0C10')
    plt.close()
    print("Generated: reports/figures/ui_eta_predictor.png")


def render_chokepoint_inspector():
    """Renders the Chokepoint Hub Inspector view."""
    fig = plt.figure(figsize=(14, 8), facecolor='#0A0C10')
    ax = fig.add_subplot(111)
    ax.set_facecolor('#0A0C10')
    ax.axis('off')

    ax.text(0.04, 0.92, "CHOKEPOINT HUB INSPECTOR // TOPOLOGICAL RISK AUDIT", color='#FF3366', fontsize=18, weight='bold')
    ax.text(0.04, 0.88, "Facility deep-dive: structural centrality, incident queues, and SLA breach volumes", color='#94A3B8', fontsize=12)

    # Hub Overview Card
    h_rect = patches.FancyBboxPatch((0.04, 0.45), 0.45, 0.38, boxstyle="round,pad=0.01,rounding_size=0.02",
                                    facecolor='#11141D', edgecolor='#FF3366', linewidth=2.0)
    ax.add_patch(h_rect)
    ax.text(0.07, 0.77, "SELECTED FACILITY: IND000000ACB", color='#FF3366', fontsize=14, weight='bold')
    ax.text(0.07, 0.73, "Gurgaon Bilaspur Master Logistics Hub (Haryana)", color='#FFFFFF', fontsize=13, weight='bold')
    
    metrics = [
        ("CHOKEPOINT RISK SCORE", "97.7 / 100", "#FF3366"),
        ("BETWEENNESS CENTRALITY", "0.214 (National Rank #1)", "#00F0FF"),
        ("HISTORICAL SLA BREACHES", "1,225 Consignments", "#FACC15"),
        ("INCIDENT ACTIVE CORRIDORS", "148 Incoming / 152 Outgoing", "#E2E8F0")
    ]
    for i, (k, v, col) in enumerate(metrics):
        yy = 0.65 - i * 0.05
        ax.text(0.07, yy, f"• {k}:", color='#94A3B8', fontsize=11, weight='bold')
        ax.text(0.28, yy, v, color=col, fontsize=11, weight='bold')

    # Bar chart of incoming corridor delays
    ax_bar = fig.add_axes([0.55, 0.48, 0.40, 0.34], facecolor='#11141D')
    corridors = ['Bhiwandi', 'Jaipur', 'Bangalore', 'Lucknow', 'Ludhiana']
    delays = [2.42, 2.15, 1.95, 1.88, 1.74]
    bars = ax_bar.barh(corridors, delays, color='#FF3366', edgecolor='#0A0C10', height=0.55)
    ax_bar.axvline(1.0, color='#00FF66', linestyle='--', label='OSRM Free-Flow Baseline (1.0x)')
    ax_bar.set_title("Incident Corridors Median Delay Ratio", color='#FFFFFF', fontsize=12, weight='bold')
    ax_bar.set_xlabel("Actual / OSRM Delay Factor", color='#94A3B8', fontsize=10)
    ax_bar.tick_params(colors='#E2E8F0')
    ax_bar.legend(loc='lower right', facecolor='#0A0C10', edgecolor='#1E293B', labelcolor='#FFFFFF')

    # Bottom Recommendation Box
    rec_rect = patches.FancyBboxPatch((0.04, 0.08), 0.91, 0.32, boxstyle="round,pad=0.01,rounding_size=0.02",
                                      facecolor='#11141D', edgecolor='#00FF66', linewidth=1.5)
    ax.add_patch(rec_rect)
    ax.text(0.07, 0.33, "SYSTEMIC INTERVENTION RECOMMENDATION", color='#00FF66', fontsize=13, weight='bold')
    rec_text = (
        "• Upgrade Priority: IMMEDIATE CRITICAL ACTION (Tier 1 National Bottleneck).\n"
        "• Root Cause Analysis: Inbound cross-dock transfer capacity is undersized by 35% during 18:00-22:00 peak.\n"
        "• Tactical Action: Enforce bypass via satellite hubs (Faridabad/Jaipur) for all Carting cargo under 500 kg.\n"
        "• Capital Action: Install dual automated cross-belt sorters (Projected impact: -40% dwell, -7.01% network late shipments)."
    )
    ax.text(0.07, 0.13, rec_text, color='#E2E8F0', fontsize=11, linespacing=1.7)

    plt.tight_layout()
    fig.savefig("reports/figures/ui_chokepoint_inspector.png", dpi=200, facecolor='#0A0C10')
    plt.close()
    print("Generated: reports/figures/ui_chokepoint_inspector.png")


def render_bypass_router():
    """Renders the Dynamic Congestion Bypass Router view."""
    fig = plt.figure(figsize=(14, 8), facecolor='#0A0C10')
    ax = fig.add_subplot(111)
    ax.set_facecolor('#0A0C10')
    ax.axis('off')

    ax.text(0.04, 0.92, "DYNAMIC BYPASS ROUTER // TMS OPTIMIZATION", color='#00FF66', fontsize=18, weight='bold')
    ax.text(0.04, 0.88, "Real-time cost-weighted Dijkstra path optimization to circumvent active chokepoints", color='#94A3B8', fontsize=12)

    # Route 1: Standard Bottleneck Route
    r1_rect = patches.FancyBboxPatch((0.04, 0.48), 0.44, 0.35, boxstyle="round,pad=0.01,rounding_size=0.02",
                                     facecolor='#11141D', edgecolor='#FF3366', linewidth=1.8)
    ax.add_patch(r1_rect)
    ax.text(0.07, 0.77, "STANDARD ROUTE (VIA BILASPUR CHOKEPOINT)", color='#FF3366', fontsize=13, weight='bold')
    ax.text(0.07, 0.70, "Origin -> Bilaspur Master Hub -> Bangalore", color='#FFFFFF', fontsize=12)
    ax.text(0.07, 0.63, "• Total Transit Time: 38.4 Hours", color='#FFFFFF', fontsize=12, weight='bold')
    ax.text(0.07, 0.57, "• Sorting Queue Dwell: 6.8 Hours", color='#FF3366', fontsize=12, weight='bold')
    ax.text(0.07, 0.51, "• SLA Breach Risk: HIGH (84% Probability)", color='#FF3366', fontsize=11, weight='bold')

    # Route 2: Recommended Bypass Route
    r2_rect = patches.FancyBboxPatch((0.51, 0.48), 0.44, 0.35, boxstyle="round,pad=0.01,rounding_size=0.02",
                                     facecolor='#11141D', edgecolor='#00FF66', linewidth=2.0)
    ax.add_patch(r2_rect)
    ax.text(0.54, 0.77, "RECOMMENDED BYPASS ROUTE (OPTIMIZED)", color='#00FF66', fontsize=13, weight='bold')
    ax.text(0.54, 0.70, "Origin -> Satellite Feeder Bypass -> Direct FTL -> Bangalore", color='#FFFFFF', fontsize=12)
    ax.text(0.54, 0.63, "• Total Transit Time: 33.1 Hours (-5.3 HOURS SAVED)", color='#00FF66', fontsize=12, weight='bold')
    ax.text(0.54, 0.57, "• Sorting Queue Dwell: 1.5 Hours", color='#00FF66', fontsize=12, weight='bold')
    ax.text(0.54, 0.51, "• SLA Breach Risk: LOW (18% Probability)", color='#00FF66', fontsize=11, weight='bold')

    # Economic Comparison Box
    eco_rect = patches.FancyBboxPatch((0.04, 0.10), 0.91, 0.32, boxstyle="round,pad=0.01,rounding_size=0.02",
                                      facecolor='#11141D', edgecolor='#00F0FF', linewidth=1.5)
    ax.add_patch(eco_rect)
    ax.text(0.07, 0.35, "DISPATCH TRADE-OFF EVALUATION", color='#00F0FF', fontsize=13, weight='bold')
    eco_text = (
        "• Mileage Delta: +42 km detour (+2.0% distance).\n"
        "• Additional Fuel/Linehaul Cost: +INR 420.\n"
        "• SLA Breach Penalty Avoided: INR 2,500 (Guaranteed on-time delivery).\n"
        "• Net Dispatch Advantage: +INR 2,080 Net Value per consignment dispatch!\n"
        "• Dispatch Engine Action: AUTOMATICALLY ROUTED VIA SATELLITE FEEDER BYPASS."
    )
    ax.text(0.07, 0.14, eco_text, color='#E2E8F0', fontsize=11, linespacing=1.7)

    plt.tight_layout()
    fig.savefig("reports/figures/ui_bypass_router.png", dpi=200, facecolor='#0A0C10')
    plt.close()
    print("Generated: reports/figures/ui_bypass_router.png")


if __name__ == "__main__":
    render_watchtower_hud()
    render_eta_predictor()
    render_chokepoint_inspector()
    render_bypass_router()
    print("All frontend UI render assets successfully generated.")
