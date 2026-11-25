"""
src/data_prep.py
----------------
Data Ingestion, Cleaning, and Segment/Trip Aggregation Pipeline for Delhivery Logistics.
Strictly ensures zero data leakage between training and testing splits.
"""

import os
import re
import numpy as np
import pandas as pd


def parse_hub_state(center_name):
    """Extract state or region from center name like 'Anand_VUNagar_DC (Gujarat)'"""
    if pd.isna(center_name):
        return "Unknown"
    match = re.search(r'\((.*?)\)', str(center_name))
    if match:
        return match.group(1).strip()
    # If no parenthesis, fallback to center name prefix
    parts = str(center_name).split('_')
    return parts[0] if parts else "Unknown"


def categorize_time_of_day(hour):
    """Categorize 24-hr hour into 4 standard operational operational periods."""
    if 6 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 18:
        return "Afternoon"
    elif 18 <= hour < 24:
        return "Evening"
    else:
        return "Night"


def categorize_distance_band(distance_km):
    """Categorize trip distance into operational logistics bands."""
    if distance_km < 100:
        return "Short (<100km)"
    elif distance_km <= 300:
        return "Medium (100-300km)"
    else:
        return "Long (>300km)"


def load_and_clean_raw_data(filepath="data/delhivery_data.csv"):
    """
    Load raw Delhivery shipment data and perform initial data sanitation:
    - Parse timestamps
    - Clean missing / anomalous rows
    - Remove invalid distances and times
    """
    print(f"Loading raw dataset from {filepath}...")
    df = pd.read_csv(filepath)
    print(f"Initial raw record count: {len(df):,}")

    # Drop completely duplicate rows if any
    df = df.drop_duplicates()

    # Fill or sanitize names
    df['source_name'] = df['source_name'].fillna("Unknown_Source")
    df['destination_name'] = df['destination_name'].fillna("Unknown_Destination")

    # Parse timestamps
    df['trip_creation_time'] = pd.to_datetime(df['trip_creation_time'], errors='coerce')
    df['od_start_time'] = pd.to_datetime(df['od_start_time'], errors='coerce')
    df['od_end_time'] = pd.to_datetime(df['od_end_time'], errors='coerce')

    # Filter out records where timestamps are missing or invalid
    df = df.dropna(subset=['od_start_time', 'od_end_time'])

    # Sanity checks on segment distances and times
    df = df[(df['segment_actual_time'] > 0) & (df['segment_osrm_time'] > 0)]
    df = df[(df['segment_osrm_distance'] >= 0)]

    print(f"Records after cleaning raw data: {len(df):,}")
    return df


def aggregate_trip_segments(df):
    """
    Aggregate scan-level records into discrete corridor segments (hops)
    between source_center and destination_center for each trip_uuid.

    Calculates:
    - actual_time_min: sum of segment_actual_time or start_scan_to_end_scan
    - osrm_time_min: sum of segment_osrm_time
    - actual_distance_km: last actual_distance_to_destination or sum of segments
    - osrm_distance_km: sum of segment_osrm_distance
    - delay_ratio: actual_time_min / osrm_time_min
    - sla_breached: indicator if delay ratio exceeds 1.25 or chronic delay
    """
    print("Aggregating trip segments into discrete corridor hops...")

    # Group by trip_uuid and OD segment
    # In Delhivery data, each OD pair in a trip represents one corridor leg.
    grouped = df.groupby(['trip_uuid', 'source_center', 'destination_center'], as_index=False).agg({
        'data': 'first',
        'route_type': 'first',
        'trip_creation_time': 'first',
        'source_name': 'first',
        'destination_name': 'first',
        'od_start_time': 'first',
        'od_end_time': 'last',
        'start_scan_to_end_scan': 'first',
        'segment_actual_time': 'sum',
        'segment_osrm_time': 'sum',
        'segment_osrm_distance': 'sum',
        'actual_distance_to_destination': 'last',
        'cutoff_factor': 'count' # number of scans/cutoffs
    })

    grouped.rename(columns={
        'segment_actual_time': 'actual_moving_time_min',
        'segment_osrm_time': 'osrm_time_min',
        'segment_osrm_distance': 'osrm_distance_km',
        'actual_distance_to_destination': 'actual_distance_km',
        'cutoff_factor': 'scan_count'
    }, inplace=True)

    # If actual_distance_km is <= 0 or missing, fallback to osrm_distance_km
    grouped['actual_distance_km'] = np.where(
        grouped['actual_distance_km'] > 0,
        grouped['actual_distance_km'],
        grouped['osrm_distance_km']
    )

    # Use actual moving time in hours for standard logistics ETA evaluation
    grouped['actual_time_hr'] = grouped['actual_moving_time_min'] / 60.0
    grouped['osrm_time_hr'] = grouped['osrm_time_min'] / 60.0
    grouped['total_scan_time_hr'] = grouped['start_scan_to_end_scan'] / 60.0

    # Delay ratio (actual moving time vs OSRM estimate)
    grouped['delay_ratio'] = grouped['actual_moving_time_min'] / grouped['osrm_time_min'].replace(0, np.nan)
    grouped = grouped.dropna(subset=['delay_ratio'])

    # Time features
    grouped['start_hour'] = grouped['od_start_time'].dt.hour
    grouped['start_dayofweek'] = grouped['od_start_time'].dt.dayofweek
    grouped['time_of_day'] = grouped['start_hour'].apply(categorize_time_of_day)
    grouped['distance_band'] = grouped['osrm_distance_km'].apply(categorize_distance_band)

    # Extract state/region metadata
    grouped['source_state'] = grouped['source_name'].apply(parse_hub_state)
    grouped['destination_state'] = grouped['destination_name'].apply(parse_hub_state)

    # Define SLA Breach:
    # In logistics operations, delivery SLA breach occurs when actual transit exceeds standard tolerance.
    # We define SLA Breach if delay_ratio > 1.25 (i.e., trip was delayed by more than 25% over OSRM SLA)
    grouped['sla_breached'] = (grouped['delay_ratio'] > 1.25).astype(int)
    grouped['is_chronic_delay'] = (grouped['delay_ratio'] > 1.20).astype(int)

    # Filter out extreme physical outliers (e.g. delay ratio > 20 or < 0.05)
    valid_mask = (grouped['delay_ratio'] >= 0.1) & (grouped['delay_ratio'] <= 15.0) & (grouped['osrm_time_min'] >= 2.0)
    grouped = grouped[valid_mask].reset_index(drop=True)

    print(f"Aggregated segment records: {len(grouped):,}")
    print(f"Training split segments: {(grouped['data'] == 'training').sum():,}")
    print(f"Test split segments: {(grouped['data'] == 'test').sum():,}")
    print(f"Overall SLA breach rate: {grouped['sla_breached'].mean() * 100:.2f}%")
    print(f"Overall Chronic delay (>20%) rate: {grouped['is_chronic_delay'].mean() * 100:.2f}%")

    return grouped


def prepare_and_save_data(raw_filepath="data/delhivery_data.csv", output_dir="data"):
    """Full execution of the data preparation stage."""
    os.makedirs(output_dir, exist_ok=True)
    df_raw = load_and_clean_raw_data(raw_filepath)
    df_segments = aggregate_trip_segments(df_raw)

    out_csv = os.path.join(output_dir, "cleaned_segments.csv")
    df_segments.to_csv(out_csv, index=False)
    print(f"Saved preprocessed segment dataset to {out_csv}")
    return df_segments


if __name__ == "__main__":
    prepare_and_save_data()

