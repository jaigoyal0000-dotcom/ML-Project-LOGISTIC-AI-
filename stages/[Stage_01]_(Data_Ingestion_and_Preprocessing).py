"""
[Stage_01]_(Data_Ingestion_and_Preprocessing).py
------------------------------------------------
STAGE 1: Ingestion, Cleaning, Segment Synthesis, and Leakage Prevention.
- Ingests raw Delhivery dataset (144k+ scans).
- Synthesizes discrete Origin-to-Destination corridor legs (26k+ segments).
- Enforces strict chronological train/test partitioning to prevent target leakage.
- Filters invalid speeds, negative durations, and sensor anomalies.
Output: data/cleaned_segments.csv
"""

import os
import sys
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data_prep import prepare_and_save_data


def run_stage():
    print("=" * 75)
    print(" [STAGE 01] DATA INGESTION, SEGMENT SYNTHESIS & LEAKAGE PREVENTION ")
    print("=" * 75)
    t0 = time.time()
    df = prepare_and_save_data()
    print(f"\n>>> Stage 01 successfully completed in {time.time() - t0:.2f}s!")
    print(f">>> Output Artifact: data/cleaned_segments.csv ({len(df):,} segments)")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    run_stage()
