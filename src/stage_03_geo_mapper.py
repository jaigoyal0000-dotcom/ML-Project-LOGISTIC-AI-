"""
src/stage_03_geo_mapper.py
--------------------------
Assigns real-world Indian geographic coordinates (latitude, longitude) to Delhivery
logistics facilities using the official GeoNames Indian Postal Code database (pgeocode)
by extracting the 6-digit PIN code from each facility hub_id (e.g., IND562132AAA -> 562132).
Falls back to 3-digit postal prefix matching and major hub references only when a hub
uses an internal non-postal code (e.g., IND000000ACB -> Gurgaon Bilaspur).
"""

import os
import re
import numpy as np
import pandas as pd
import pgeocode

# Reference coordinates for internal non-PIN master hubs (e.g. IND000000*)
INTERNAL_CITY_COORDS = {
    "gurgaon": (28.4595, 77.0266),
    "bilaspur": (28.3245, 76.8483),
    "delhi": (28.6139, 77.2090),
    "bhiwandi": (19.2967, 73.0631),
    "mumbai": (19.0760, 72.8777),
    "bangalore": (12.9716, 77.5946),
    "bengaluru": (12.9716, 77.5946),
    "nelamangala": (13.0984, 77.3917),
    "hyderabad": (17.3850, 78.4867),
    "shamshabad": (17.2662, 78.3970),
    "kolkata": (22.5726, 88.3639),
    "dankuni": (22.6841, 88.2917),
    "chennai": (13.0827, 80.2707),
    "ahmedabad": (23.0225, 72.5714),
    "pune": (18.5204, 73.8567),
}


def enrich_hubs_with_geocoordinates(
    hubs_csv="data/hub_centrality_metrics.csv",
    output_csv="data/hubs_geocoded.csv"
):
    """Reads hub centrality metrics and enriches each facility with real GeoNames lat/lon."""
    print("Geocoding logistics facilities using real GeoNames India Postal Database (pgeocode)...")
    df = pd.read_csv(hubs_csv)
    nomi = pgeocode.Nominatim("in")

    # Extract 6-digit PIN from hub_id (e.g., IND562132AAA -> 562132)
    pins = df["hub_id"].astype(str).str.extract(r"IND(\d{6})")[0]
    unique_pins = [p for p in pins.dropna().unique() if p != "000000"]

    geo_df = nomi.query_postal_code(unique_pins)
    pin_to_coords = {}
    for pin, lat, lon in zip(unique_pins, geo_df["latitude"], geo_df["longitude"]):
        if pd.notna(lat) and pd.notna(lon):
            pin_to_coords[pin] = (float(lat), float(lon))

    # Build 3-digit postal prefix fallback from real GeoNames data
    prefix_df = nomi._data[["postal_code", "latitude", "longitude"]].dropna().copy()
    prefix_df["prefix3"] = prefix_df["postal_code"].astype(str).str[:3]
    prefix_means = prefix_df.groupby("prefix3")[["latitude", "longitude"]].mean().to_dict("index")

    lats, lons, sources = [], [], []
    for idx, row in df.iterrows():
        hub_id = str(row["hub_id"])
        name_str = str(row["hub_name"]).lower()
        pin = pins.iloc[idx]

        # 1. Exact 6-digit GeoNames PIN lookup
        if pd.notna(pin) and pin in pin_to_coords:
            lat, lon = pin_to_coords[pin]
            lats.append(lat)
            lons.append(lon)
            sources.append("GeoNames_PIN")
            continue

        # 2. Internal master hub city lookup (e.g. IND000000ACB Gurgaon Bilaspur)
        matched_city = False
        for city, (lat, lon) in INTERNAL_CITY_COORDS.items():
            if city in name_str:
                lats.append(lat)
                lons.append(lon)
                sources.append("City_Reference")
                matched_city = True
                break
        if matched_city:
            continue

        # 3. Real GeoNames 3-digit postal region centroid fallback
        if pd.notna(pin) and pin != "000000" and pin[:3] in prefix_means:
            m = prefix_means[pin[:3]]
            lats.append(float(m["latitude"]))
            lons.append(float(m["longitude"]))
            sources.append("GeoNames_Prefix3")
            continue

        # 4. Geographic center of India fallback
        lats.append(21.1458)
        lons.append(79.0882)
        sources.append("India_Center")

    df["latitude"] = lats
    df["longitude"] = lons
    df["geo_source"] = sources

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"Saved real geocoded hubs ({len(df):,} locations) to {output_csv}")
    print("Geocoding Source Breakdown:", df["geo_source"].value_counts().to_dict())
    return df


if __name__ == "__main__":
    enrich_hubs_with_geocoordinates()
