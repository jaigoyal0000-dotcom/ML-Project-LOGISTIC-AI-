"""
[Stage_03]_(Geospatial_Mapping_and_Coordinates).py
---------------------------------------------------
STAGE 3: Facility Spatial Mapping & Indian Geocoding.
- Enriches all 1,589 logistics hubs with verified Indian latitude and longitude coordinates.
- Enables spatial map layers, distance validation, and Leaflet interactive visualization.
Output: data/hubs_geocoded.csv
"""

import os
import sys
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.geo_mapper import enrich_hubs_with_geocoordinates


def run_stage():
    print("=" * 75)
    print(" [STAGE 03] LOGISTICS FACILITY GEOSPATIAL COORDINATES MAPPING ")
    print("=" * 75)
    t0 = time.time()
    df = enrich_hubs_with_geocoordinates()
    print(f"\n>>> Stage 03 successfully completed in {time.time() - t0:.2f}s!")
    print(f">>> Geocoded {len(df):,} facilities across Indian states and union territories.")
    print(">>> Output Artifact: data/hubs_geocoded.csv")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    run_stage()
