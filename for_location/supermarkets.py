import time
import math
import requests
from collections import deque

# ── CONFIG ─────────────────────────────────────────────────────────────────────

API_KEY        = "API_Key"
SW_LAT, SW_LNG = 41.6100, 44.7000   # SW corner of Tbilisi
NE_LAT, NE_LNG = 41.8400, 44.9500   # NE corner of Tbilisi

INITIAL_RADIUS = 1500    # meters
MIN_RADIUS     = 300     # meters
TYPE           = "supermarket"  # Google Places type for supermarkets

# ── GRID & ADAPTIVE SUBDIVISION ────────────────────────────────────────────────

def generate_grid(sw_lat, sw_lng, ne_lat, ne_lng, radius):
    """Build a uniform grid of (lat, lng, radius) covering the bbox."""
    lat_step = (radius * 2) / 111000.0
    pts = []
    lat = sw_lat
    while lat <= ne_lat:
        lng_step = (radius * 2) / (111000.0 * math.cos(math.radians(lat)))
        lng = sw_lng
        while lng <= ne_lng:
            pts.append((lat, lng, radius))
            lng += lng_step
        lat += lat_step
    return pts

def subdivide_center(lat, lng, radius):
    """
    Split one search circle into four half-radius circles
    at NE, NW, SE, SW for adaptive refinement.
    """
    new_r = radius / 2.0
    dlat = new_r / 111000.0
    dlng = new_r / (111000.0 * math.cos(math.radians(lat)))
    return [
        (lat + dlat, lng + dlng, new_r),
        (lat + dlat, lng - dlng, new_r),
        (lat - dlat, lng + dlng, new_r),
        (lat - dlat, lng - dlng, new_r),
    ]

# ── GOOGLE PLACES NEARBY SEARCH WITH PAGINATION ─────────────────────────────────

def nearby_search(lat, lng, radius):
    """
    Perform a paginated Google Places Nearby Search for supermarkets.
    """
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key": API_KEY,
        "location": f"{lat},{lng}",
        "radius": int(radius),
        "type": TYPE
    }
    places = []
    while True:
        resp = requests.get(url, params=params).json()
        places.extend(resp.get("results", []))
        token = resp.get("next_page_token")
        if not token:
            break
        time.sleep(2)  # wait for next_page_token to activate
        params = {"key": API_KEY, "pagetoken": token}
    return places

# ── MAIN COLLECTION ─────────────────────────────────────────────────────────────

def collect_all_supermarkets():
    centers = deque(generate_grid(SW_LAT, SW_LNG, NE_LAT, NE_LNG, INITIAL_RADIUS))
    supermarkets = {}

    while centers:
        lat, lng, rad = centers.popleft()
        results = nearby_search(lat, lng, rad)

        # If this search returned the cap (60) and we can subdivide, refine
        if len(results) >= 60 and rad > MIN_RADIUS:
            centers.extend(subdivide_center(lat, lng, rad))
            continue

        for p in results:
            pid   = p["place_id"]
            types = p.get("types", [])
            name  = p.get("name", "")

            # Only keep true supermarkets
            if "supermarket" not in types:
                continue
            # Exclude convenience or small corner stores
            if "convenience_store" in types:
                continue

            if pid not in supermarkets:
                loc = p["geometry"]["location"]
                supermarkets[pid] = {
                    "place_id": pid,
                    "name": name,
                    "latitude": loc["lat"],
                    "longitude": loc["lng"]
                }

    return list(supermarkets.values())

if __name__ == "__main__":
    all_supers = collect_all_supermarkets()
    print(f"Total supermarkets found: {len(all_supers)}")

    # Optionally save results to CSV
    import pandas as pd
    pd.DataFrame(all_supers).to_csv("tbilisi_supermarkets.csv", index=False)
