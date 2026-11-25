"""
src/geo_mapper.py
-----------------
Assigns realistic Indian geographic coordinates (latitude, longitude) to Delhivery
logistics facilities based on city names, state names, and PIN center codes.
Produces geospatial layers for interactive map visualizations and routing.
"""

import os
import re
import numpy as np
import pandas as pd

# High-precision reference coordinates for major Indian logistics centers and states
CITY_COORDINATES = {
    "gurgaon": (28.4595, 77.0266),
    "bilaspur": (28.3245, 76.8483),
    "delhi": (28.6139, 77.2090),
    "sonipat": (28.9931, 77.0151),
    "chandigarh": (30.7333, 76.7794),
    "ludhiana": (30.9010, 75.8573),
    "jaipur": (26.9124, 75.7873),
    "lucknow": (26.8467, 80.9462),
    "kanpur": (26.4499, 80.3319),
    "patna": (25.5941, 85.1376),
    "muzaffarpur": (26.1209, 85.3647),
    "kolkata": (22.5726, 88.3639),
    "dankuni": (22.6841, 88.2917),
    "guwahati": (26.1445, 91.7362),
    "ahmedabad": (23.0225, 72.5714),
    "surat": (21.1702, 72.8311),
    "vadodara": (22.3072, 73.1812),
    "mumbai": (19.0760, 72.8777),
    "bhiwandi": (19.2967, 73.0631),
    "pune": (18.5204, 73.8567),
    "nagpur": (21.1458, 79.0882),
    "indore": (22.7196, 75.8577),
    "bhopal": (23.2599, 77.4126),
    "hyderabad": (17.3850, 78.4867),
    "shamshabad": (17.2662, 78.3970),
    "bangalore": (12.9716, 77.5946),
    "bengaluru": (12.9716, 77.5946),
    "nelamangala": (13.0984, 77.3917),
    "bommasandra": (12.8167, 77.6833),
    "chennai": (13.0827, 80.2707),
    "poonamallee": (13.0489, 80.0967),
    "coimbatore": (11.0168, 76.9558),
    "kochi": (9.9312, 76.2673),
    "ernakulam": (9.9816, 76.2999)
}

STATE_CENTROIDS = {
    "haryana": (29.0588, 76.0856),
    "delhi": (28.7041, 77.1025),
    "punjab": (31.1471, 75.3412),
    "rajasthan": (27.0238, 74.2179),
    "uttar pradesh": (26.8467, 80.9462),
    "bihar": (25.0961, 85.3131),
    "west bengal": (22.9868, 87.8550),
    "assam": (26.2006, 92.9376),
    "gujarat": (22.2587, 71.1924),
    "maharashtra": (19.7515, 75.7139),
    "madhya pradesh": (22.9734, 78.6569),
    "telangana": (18.1124, 79.0193),
    "andhra pradesh": (15.9129, 79.7400),
    "karnataka": (15.3173, 75.7139),
    "tamil nadu": (11.1271, 78.6569),
    "kerala": (10.8505, 76.2711),
    "odisha": (20.9517, 85.0985)
}


def geocode_hub(hub_id, hub_name, hub_state):
    """Derives latitude and longitude for a logistics center."""
    name_str = str(hub_name).lower()
    state_str = str(hub_state).lower()

    # 1. Check specific city keywords
    for city, (lat, lon) in CITY_COORDINATES.items():
        if city in name_str:
            # Add small deterministic jitter based on hub_id hash so hubs in same city don't completely overlap
            seed = sum(ord(c) for c in hub_id) % 100
            jitter_lat = ((seed % 10) - 5) * 0.012
            jitter_lon = (((seed // 10) % 10) - 5) * 0.012
            return lat + jitter_lat, lon + jitter_lon

    # 2. Check state centroid
    for state, (lat, lon) in STATE_CENTROIDS.items():
        if state in state_str or state in name_str:
            seed = sum(ord(c) for c in hub_id) % 1000
            jitter_lat = ((seed % 20) - 10) * 0.04
            jitter_lon = (((seed // 20) % 20) - 10) * 0.04
            return lat + jitter_lat, lon + jitter_lon

    # 3. Fallback to geographic center of India
    seed = sum(ord(c) for c in hub_id) % 1000
    return 21.0 + ((seed % 20) - 10) * 0.1, 78.0 + (((seed // 20) % 20) - 10) * 0.1


def enrich_hubs_with_geocoordinates(hubs_csv="data/hub_centrality_metrics.csv", output_csv="data/hubs_geocoded.csv"):
    """Reads hub centrality metrics and writes an enriched dataset with lat and lon."""
    print("Geocoding logistics facilities across India...")
    df = pd.read_csv(hubs_csv)

    coords = [geocode_hub(r['hub_id'], r['hub_name'], r['hub_state']) for _, r in df.iterrows()]
    df['latitude'] = [c[0] for c in coords]
    df['longitude'] = [c[1] for c in coords]

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"Saved geocoded hubs ({len(df):,} locations) to {output_csv}")
    return df


if __name__ == "__main__":
    enrich_hubs_with_geocoordinates()
