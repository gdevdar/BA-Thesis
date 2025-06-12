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
TYPE           = "school"   # we use type=school to catch tagged kindergartens

# ── GRID & ADAPTIVE SUBDIVISION ────────────────────────────────────────────────

def generate_grid(sw_lat, sw_lng, ne_lat, ne_lng, radius):
    """Build a uniform grid of (lat, lng, radius) covering the box."""
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
    """Split one cell into four half-radius cells (NE, NW, SE, SW)."""
    new_r = radius / 2.0
    dlat = new_r / 111000.0
    dlng = new_r / (111000.0 * math.cos(math.radians(lat)))
    return [
        (lat + dlat, lng + dlng, new_r),
        (lat + dlat, lng - dlng, new_r),
        (lat - dlat, lng + dlng, new_r),
        (lat - dlat, lng - dlng, new_r),
    ]

# ── GOOGLE PLACES NEARBY SEARCH w/ PAGINATION ──────────────────────────────────

def nearby_search(lat, lng, radius):
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
        time.sleep(2)  # allow token activation
        params = {"key": API_KEY, "pagetoken": token}
    return places

# ── MAIN COLLECTION ─────────────────────────────────────────────────────────────

def collect_all_kindergartens():
    centers = deque(generate_grid(SW_LAT, SW_LNG, NE_LAT, NE_LNG, INITIAL_RADIUS))
    kinders = {}  # place_id → data

    while centers:
        lat, lng, rad = centers.popleft()
        results = nearby_search(lat, lng, rad)

        # if maxed out (60) and still large, subdivide
        if len(results) >= 60 and rad > MIN_RADIUS:
            centers.extend(subdivide_center(lat, lng, rad))
            continue

        for p in results:
            pid   = p["place_id"]
            types = p.get("types", [])
            name  = p.get("name", "").lower()

            # Must be a kindergarten — name or type indicates it
            if not (
                "kindergarten" in name
                or "ბაღ" in name               # Georgian
                or "детский" in name           # Russian
                or "child_care" in types
                or "day_care" in types
            ):
                continue

            # Exclude any universities or standard schools
            if "university" in types or "college" in types:
                continue

            # Deduplicate
            if pid not in kinders:
                loc = p["geometry"]["location"]
                kinders[pid] = {
                    "place_id": pid,
                    "name": p["name"],
                    "latitude": loc["lat"],
                    "longitude": loc["lng"]
                }

    return list(kinders.values())

if __name__ == "__main__":
    all_kinders = collect_all_kindergartens()
    print(f"Total kindergartens found: {len(all_kinders)}")

    # Optionally save to CSV
    import pandas as pd
    pd.DataFrame(all_kinders).to_csv("tbilisi_kindergartens.csv", index=False)
