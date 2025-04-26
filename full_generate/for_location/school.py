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
TYPE           = "school"

# ── GRID & ADAPTIVE SUBDIVISION ────────────────────────────────────────────────

def generate_grid(sw_lat, sw_lng, ne_lat, ne_lng, radius):
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

def collect_all_k12_schools():
    centers = deque(generate_grid(SW_LAT, SW_LNG, NE_LAT, NE_LNG, INITIAL_RADIUS))
    schools = {}  # place_id → data

    while centers:
        lat, lng, rad = centers.popleft()
        results = nearby_search(lat, lng, rad)

        # if maxed out, subdivide (unless already very small)
        if len(results) >= 60 and rad > MIN_RADIUS:
            centers.extend(subdivide_center(lat, lng, rad))
            continue

        for p in results:
            pid   = p["place_id"]
            types = p.get("types", [])
            name  = p.get("name", "").lower()

            # Exclude higher-ed
            if "university" in types or "college" in types:
                continue
            # Exclude kindergartens
            if "kindergarten" in name or "ბაღ" in name or "детский" in name:
                continue
            if "child_care" in types or "day_care" in types:
                continue

            # Accept everything else under type=school
            if pid not in schools:
                loc = p["geometry"]["location"]
                schools[pid] = {
                    "place_id": pid,
                    "name": p["name"],
                    "latitude": loc["lat"],
                    "longitude": loc["lng"]
                }

    return list(schools.values())

if __name__ == "__main__":
    all_schools = collect_all_k12_schools()
    print(f"Collected {len(all_schools)} K–12 schools in Tbilisi")
    # Save to CSV
    import pandas as pd
    pd.DataFrame(all_schools).to_csv("tbilisi_k12_schools.csv", index=False)
