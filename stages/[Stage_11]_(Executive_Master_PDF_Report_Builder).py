"""
[Stage_11]_(Executive_Master_PDF_Report_Builder).py
---------------------------------------------------
STAGE 11: Master Project Report PDF Generator (ReportLab).
- Generates 1.87 MB publication-grade master report PDF.
- Includes Executive Summary, Tech Stack Table, Methodology, Benchmarks, ROI Model, and Viva Q&A.
Output: reports/Delhivery_Logistics_Optimization_Full_Project_Report.pdf
"""

import os
import sys
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.master_report_pdf import build_master_pdf


def run_stage():
    print("=" * 75)
    print(" [STAGE 11] EXECUTIVE MASTER PDF REPORT BUILDER ")
    print("=" * 75)
    t0 = time.time()
    pdf_path = build_master_pdf()
    print(f"\n>>> Stage 11 successfully completed in {time.time() - t0:.2f}s!")
    print(f">>> Output Artifact: {pdf_path}")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    run_stage()
