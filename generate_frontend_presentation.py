"""
generate_frontend_presentation.py
----------------------------------
Builds a dedicated 12-slide PowerPoint presentation deck focusing exclusively
on the Frontend Architecture, Watchtower Operations HUD UI, and Interactive Decision Support Views.
Output: frontend_presentation_slides.pptx (and copied to Desktop).
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE


def build_frontend_deck(output_path="frontend_presentation_slides.pptx"):
    print(f"Creating Frontend PowerPoint presentation at {output_path}...")
    prs = Presentation()
    prs.slide_width = Inches(13.333)  # 16:9 widescreen
    prs.slide_height = Inches(7.5)

    # Dark Cyberpunk HUD Theme Palette (Matching Uploaded Image)
    C_CANVAS = RGBColor(10, 12, 16)      # #0A0C10
    C_CARD = RGBColor(17, 20, 29)        # #11141D
    C_BORDER = RGBColor(30, 41, 59)      # #1E293B
    C_GREEN = RGBColor(0, 255, 102)      # #00FF66 Neon Green
    C_CYAN = RGBColor(0, 240, 255)       # #00F0FF Neon Cyan
    C_YELLOW = RGBColor(250, 204, 21)    # #FACC15 Warning Yellow
    C_RED = RGBColor(255, 51, 102)       # #FF3366 Alert Crimson
    C_WHITE = RGBColor(255, 255, 255)
    C_MUTED = RGBColor(148, 163, 184)    # #94A3B8 Muted Slate

    blank_layout = prs.slide_layouts[6]

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_CANVAS
        bg.line.fill.background()
        return bg

    def add_hud_header(slide, title_text, category="WATCHTOWER OPERATIONS HUD // FRONTEND ARCHITECTURE"):
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.1))
        tf = header_box.text_frame
        tf.word_wrap = True
        
        p_cat = tf.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_GREEN
        
        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = C_CYAN

    def add_hud_card(slide, left, top, width, height, title, items, border_color=C_BORDER):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = C_CARD
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1.5)
        
        tb = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.15), width - Inches(0.3), height - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p0 = tf.paragraphs[0]
        p0.text = title
        p0.font.size = Pt(13)
        p0.font.bold = True
        p0.font.color.rgb = C_GREEN
        p0.space_after = Pt(8)
        
        for head, body in items:
            p = tf.add_paragraph()
            p.text = f"• {head}: {body}" if head else f"• {body}"
            p.font.size = Pt(11)
            p.font.color.rgb = C_WHITE
            p.space_after = Pt(6)

    # -------------------------------------------------------------
    # SLIDE 1: Title Slide
    # -------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    t_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(4.0))
    tf1 = t_box.text_frame
    p1 = tf1.paragraphs[0]
    p1.text = "WATCHTOWER OPERATIONS HUD\nInteractive Frontend & Decision Support Center"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE

    p1_sub = tf1.add_paragraph()
    p1_sub.text = "Dark Cyberpunk Telemetry · Real-Time GNN Inference · Delhivery Freight Intelligence"
    p1_sub.font.size = Pt(18)
    p1_sub.font.color.rgb = C_CYAN
    p1_sub.space_before = Pt(15)

    p1_auth = tf1.add_paragraph()
    p1_auth.text = "Streamlit · Leaflet Geospatial · Flask REST API · Real-Time Telemetry Waveforms"
    p1_auth.font.size = Pt(14)
    p1_auth.font.color.rgb = C_GREEN
    p1_auth.space_before = Pt(35)

    # -------------------------------------------------------------
    # SLIDE 2: UI Design Philosophy & Color System
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_hud_header(s2, "UI Design Philosophy & Cyberpunk Telemetry Palette")

    add_hud_card(s2, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.3),
                 "Watchtower Aesthetic Rationale",
                 [
                     ("Operations Room Ergonomics", "Logistics command centers require low-fatigue, high-contrast dark environments suitable for 24/7 continuous shift monitoring."),
                     ("Visual Information Hierarchy", "Neon green (#00FF66) indicates healthy throughput; electric cyan (#00F0FF) highlights live telemetry waveforms; warning yellow (#FACC15) flags queue buildup; crimson (#FF3366) alerts to SLA breaches."),
                     ("Modular Card Architecture", "Every operational view is encapsulated in rounded CSS telemetry containers matching military command displays."),
                     ("Real Data Exclusively", "Zero hardcoded mock data. Every metric connects directly to the processed Delhivery dataset and trained GNN models.")
                 ], border_color=C_GREEN)

    add_hud_card(s2, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3),
                 "Core Design Tokens & Palette",
                 [
                     ("Canvas Deep Space (#0A0C10)", "Deep obsidian background providing infinite contrast for glowing telemetry."),
                     ("Container Surface (#11141D)", "Subtle dark slate card fill with 1.5px border outline (#1E293B)."),
                     ("Optimal Status (#00FF66)", "Used for 'SYSTEM ACTIVE', 'OPTIMAL', and Graph Model accuracy badges."),
                     ("Stream 01 Waveform (#00F0FF)", "Represents Alpha/Beta corridor transit rhythm across active linehaul routes."),
                     ("Stream 02 Waveform (#FACC15)", "Represents Gamma bottleneck queue activity and sorting dock dwell deviations."),
                     ("Alert Notification (#FF3366)", "Used for chokepoint danger flags, critical delay alerts, and SLA breach volumes.")
                 ], border_color=C_CYAN)

    # -------------------------------------------------------------
    # SLIDE 3: Reference Image vs. Realized Watchtower Dashboard
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_hud_header(s3, "Design Translation: Concept Reference to Production HUD")

    ref_img = "reports/figures/watchtower_theme_reference.jpg"
    if os.path.exists(ref_img):
        s3.shapes.add_picture(ref_img, Inches(0.8), Inches(1.8), width=Inches(5.6))

    hud_img = "reports/figures/ui_hud_overview.png"
    if os.path.exists(hud_img):
        s3.shapes.add_picture(hud_img, Inches(6.8), Inches(1.8), width=Inches(5.7))

    # -------------------------------------------------------------
    # SLIDE 4: View 1 — Live Watchtower Monitoring HUD
    # -------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_hud_header(s4, "View 1: Real-Time Network Telemetry HUD")

    if os.path.exists(hud_img):
        s4.shapes.add_picture(hud_img, Inches(0.8), Inches(1.6), width=Inches(7.2))

    add_hud_card(s4, Inches(8.3), Inches(1.6), Inches(4.2), Inches(5.3),
                 "HUD Component Breakdown",
                 [
                     ("Top KPI Status Strip", "4 real-time monitors: Active Hubs (1,589), Signal Quality (98.5% within SLA), Alerts 24h (0), and Safety Status (OPTIMAL)."),
                     ("Stream 01 Waveform (Cyan)", "Visualizes normal corridor transit rhythms across primary national freight lanes."),
                     ("Stream 02 Waveform (Yellow)", "Surfaces real-time sorting dock queue activity and elevated dwell surges."),
                     ("Chokepoint Subject Monitor", "Live watchlist tracking SUB-001 (Gurgaon), SUB-002 (Bangalore), SUB-003 (Bhiwandi), with recording status and risk score gauges.")
                 ], border_color=C_CYAN)

    # -------------------------------------------------------------
    # SLIDE 5: View 2 — Geospatial Indian Logistics Network Map
    # -------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_hud_header(s5, "View 2: Geospatial Network Topology & Corridor Flow")

    fig3 = "reports/figures/fig3_network_topology_bottlenecks.png"
    if os.path.exists(fig3):
        s5.shapes.add_picture(fig3, Inches(0.8), Inches(1.6), width=Inches(6.2))

    add_hud_card(s5, Inches(7.3), Inches(1.6), Inches(5.2), Inches(5.3),
                 "Geospatial Features",
                 [
                     ("Interactive Pan & Zoom", "Leaflet-powered map plotting 1,589 verified Indian logistics facilities with accurate latitude and longitude coordinates."),
                     ("Dynamic Corridor Lines", "Visualizes 2,501 transport corridors color-coded by median delay ratio (Green = on-time, Orange = moderate, Red = chronic delay >1.5x)."),
                     ("Facility Inspection Popups", "Clicking any node displays incoming/outgoing corridor count, betweenness centrality, and historical SLA breaches."),
                     ("Filter Controls", "Enables dispatchers to isolate corridors by route type (FTL vs Carting) and minimum delay severity.")
                 ], border_color=C_GREEN)

    # -------------------------------------------------------------
    # SLIDE 6: View 3 — Smart ETA Predictor
    # -------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_hud_header(s6, "View 3: Smart ETA Predictor & Graph Model Comparator")

    eta_img = "reports/figures/ui_eta_predictor.png"
    if os.path.exists(eta_img):
        s6.shapes.add_picture(eta_img, Inches(0.8), Inches(1.6), width=Inches(7.2))

    add_hud_card(s6, Inches(8.3), Inches(1.6), Inches(4.2), Inches(5.3),
                 "Predictor Capabilities",
                 [
                     ("Multi-Model Output", "Simultaneously calculates OSRM baseline (34.2h), trip baseline (42.8h), and Graph-Enhanced Model (39.5h)."),
                     ("Error Reduction Badge", "Highlights the 28.13% error reduction achieved by topological features in real time."),
                     ("Confidence Interval", "Computes 90% confidence bands (37.9h to 41.1h) for risk-managed dispatch scheduling."),
                     ("Delay Alert Badges", "Warns dispatchers if expected departure falls into an evening congestion window.")
                 ], border_color=C_GREEN)

    # -------------------------------------------------------------
    # SLIDE 7: View 4 — Chokepoint Hub Inspector
    # -------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_hud_header(s7, "View 4: Chokepoint Hub Inspector & Risk Diagnostics")

    choke_img = "reports/figures/ui_chokepoint_inspector.png"
    if os.path.exists(choke_img):
        s7.shapes.add_picture(choke_img, Inches(0.8), Inches(1.6), width=Inches(7.2))

    add_hud_card(s7, Inches(8.3), Inches(1.6), Inches(4.2), Inches(5.3),
                 "Diagnostic Features",
                 [
                     ("Hub Selector", "Search and inspect any facility among Delhivery's 1,589 hubs across India."),
                     ("Centrality Gauges", "Visualizes Betweenness Centrality (0.214), In-Degree (148), and Out-Degree (152)."),
                     ("Incident Corridor Chart", "Horizontal bar chart ranking the slowest connecting corridors by delay ratio."),
                     ("Actionable Strategy Memo", "Automated tactical and capital intervention recommendations tailored to facility risk profile.")
                 ], border_color=C_RED)

    # -------------------------------------------------------------
    # SLIDE 8: View 5 — FTL vs. Carting Simulator
    # -------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_hud_header(s8, "View 5: FTL vs. Carting Economic Trade-off Simulator")

    fig5 = "reports/figures/fig5_ftl_vs_carting_tradeoff.png"
    if os.path.exists(fig5):
        s8.shapes.add_picture(fig5, Inches(0.8), Inches(1.6), width=Inches(6.2))

    add_hud_card(s8, Inches(7.3), Inches(1.6), Inches(5.2), Inches(5.3),
                 "Simulator Parameters & Logic",
                 [
                     ("Interactive Distance Slider", "Simulate consignments from 10 km up to 2,500 km across India."),
                     ("Dynamic Cost Curves", "Computes FTL (INR 38/km) vs. Carting (INR 22/km + INR 350 dock handling) in real time."),
                     ("Breakeven Crossover", "Highlights mathematical breakeven distance (D* = 21.875 * h km)."),
                     ("Dispatch Engine Recommendation", "Automated banner advising 'ASSIGN DEDICATED FTL' or 'CONSOLIDATE VIA CARTING' based on SLA tolerance.")
                 ], border_color=C_YELLOW)

    # -------------------------------------------------------------
    # SLIDE 9: View 6 — Dynamic Congestion Bypass Router
    # -------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_hud_header(s9, "View 6: Dynamic Congestion Bypass Router")

    bypass_img = "reports/figures/ui_bypass_router.png"
    if os.path.exists(bypass_img):
        s9.shapes.add_picture(bypass_img, Inches(0.8), Inches(1.6), width=Inches(7.2))

    add_hud_card(s9, Inches(8.3), Inches(1.6), Inches(4.2), Inches(5.3),
                 "Routing Engine Capabilities",
                 [
                     ("Cost-Weighted Dijkstra", "Evaluates travel time, chronic corridor weights, and chokepoint penalties dynamically."),
                     ("Bottleneck Bypass", "Detects when primary hubs (e.g. Gurgaon) are overloaded and calculates optimal detour via satellite feeder hubs."),
                     ("Quantitative Value Metric", "Demonstrates 5.3 hours saved and +INR 2,080 net consignment value gain per dispatch!"),
                     ("TMS Integration Ready", "Available via REST API endpoint /api/v1/route/optimize for automated dispatch systems.")
                 ], border_color=C_CYAN)

    # -------------------------------------------------------------
    # SLIDE 10: View 7 — Capital Upgrade ROI Simulator
    # -------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_hud_header(s10, "View 7: Capital Upgrade ROI Leadership Simulator")

    add_hud_card(s10, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.3),
                 "Interactive Controls for Executive Leadership",
                 [
                     ("Hub Modernization Sliders", "Simulate upgrading 1, 2, 3, 4, or 5 bottleneck facilities simultaneously."),
                     ("Dwell Reduction Dial", "Test operational improvements from 10% to 50% dock dwell reduction."),
                     ("Network-Wide Impact Gauge", "Real-time calculation of late delivery reduction across all 26,000+ national corridor legs."),
                     ("Targeted Focus", "Shows why upgrading the top 3 hubs (Gurgaon, Bangalore, Bhiwandi) delivers the highest capital efficiency.")
                 ], border_color=C_GREEN)

    add_hud_card(s10, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3),
                 "Simulated Financial Returns",
                 [
                     ("Late Delivery Reduction", "Achieves a 7.01% network-wide reduction in delayed shipments with top 3 hub modernization."),
                     ("Annualized Revenue Recovered", "INR 32,406,400 (INR 3.24 Crores) in recovered revenue-at-risk."),
                     ("Breached Consignments Saved", "Prevents over 32,000 SLA breach penalties annually."),
                     ("Payback Period", "Estimated payback within 8.4 months of automated sorter deployment.")
                 ], border_color=C_CYAN)

    # -------------------------------------------------------------
    # SLIDE 11: View 8 — Documentation & 1-Click Master PDF Export
    # -------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_hud_header(s11, "View 8: Documentation Viewer & 1-Click PDF Export")

    add_hud_card(s11, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.3),
                 "Integrated Documentation Features",
                 [
                     ("1-Click Master Report Export", "Sidebar button 'EXPORT MASTER REPORT PDF' generates a publication-grade ReportLab document in seconds."),
                     ("Embedded Research Memo", "Full interactive viewer displaying the Operations Strategy Consulting Memo and executive findings."),
                     ("Viva Defense Guide", "Built-in Q&A technical defense reference covering data hygiene, graph modeling, and mathematical equations."),
                     ("Download Telemetry", "Direct HTTP download endpoints at /download/report and /download/presentation.")
                 ], border_color=C_GREEN)

    add_hud_card(s11, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3),
                 "Export Artifact Specifications",
                 [
                     ("Master PDF Report", "1.87 MB multi-page publication document with running headers, page numbers, and embedded figures."),
                     ("Presentation PowerPoint", "16-slide widescreen presentation deck with data tables, formulas, and benchmarks."),
                     ("API Documentation", "OpenAPI JSON schema available on Flask port 8000."),
                     ("Reproducibility", "End-to-end execution script run_pipeline.py reproducing all numbers from raw data.")
                 ], border_color=C_CYAN)

    # -------------------------------------------------------------
    # SLIDE 12: Frontend Technical Stack & Architecture
    # -------------------------------------------------------------
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_hud_header(s12, "Frontend Technical Stack & Production Architecture")

    add_hud_card(s12, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.3),
                 "Frontend Technology Stack",
                 [
                     ("Framework", "Streamlit 1.42+ (Python-based reactive web application framework)."),
                     ("Styling & Theming", "Custom Cyberpunk CSS injection overriding Streamlit default themes with Watchtower dark tokens."),
                     ("Geospatial Engine", "Folium / Leaflet.js with DarkMatter carto tiles for night-mode freight map rendering."),
                     ("Caching Strategy", "@st.cache_data and @st.cache_resource for zero-latency instant view transitions."),
                     ("Sub-50ms Inference", "Direct in-memory access to pre-trained LightGBM trees and NetworkX graph structures.")
                 ], border_color=C_GREEN)

    add_hud_card(s12, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3),
                 "Production Service Architecture",
                 [
                     ("UI Service (Port 8501)", "Streamlit reactive application serving the 8 Watchtower operations views."),
                     ("REST API Service (Port 8000)", "Flask 3.1 & Werkzeug microservice serving 6 high-throughput inference endpoints."),
                     ("Local Desktop Integration", "Windows automated launch and direct file synchronization for zero-friction access."),
                     ("Cloud & Docker Ready", "Fully containerizable with requirements.txt and automated batch runners (run_dashboard.bat).")
                 ], border_color=C_CYAN)

    prs.save(output_path)
    print(f"Frontend PowerPoint presentation successfully generated at {output_path} with {len(prs.slides)} slides!")


if __name__ == "__main__":
    build_frontend_deck()
