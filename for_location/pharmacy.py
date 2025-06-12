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
TYPE           = "pharmacy"

# ── GRID & ADAPTIVE SUBDIVISION ────────────────────────────────────────────────

def generate_grid(sw_lat, sw_lng, ne_lat, ne_lng, radius):
    """Build a uniform grid of (lat, lng, radius) covering the bounding box."""
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
    Split one circular cell into four smaller ones (NE, NW, SE, SW)
    at half the radius, for denser coverage where needed.
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

# ── GOOGLE PLACES NEARBY SEARCH w/ PAGINATION ──────────────────────────────────

def nearby_search(lat, lng, radius):
    """
    Perform a paginated Nearby Search for pharmacies around (lat, lng).
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
        time.sleep(2)  # give Google time to prepare the next page
        params = {"key": API_KEY, "pagetoken": token}
    return places

# ── MAIN COLLECTION ─────────────────────────────────────────────────────────────

def collect_all_pharmacies():
    centers = deque(generate_grid(SW_LAT, SW_LNG, NE_LAT, NE_LNG, INITIAL_RADIUS))
    pharmacies = {}

    while centers:
        lat, lng, rad = centers.popleft()
        results = nearby_search(lat, lng, rad)

        # If results hit the 60-result cap and radius is still above MIN_RADIUS, subdivide
        if len(results) >= 60 and rad > MIN_RADIUS:
            centers.extend(subdivide_center(lat, lng, rad))
            continue

        for p in results:
            pid   = p["place_id"]
            types = p.get("types", [])
            name  = p.get("name", "")

            # Only keep true pharmacies
            if "pharmacy" not in types:
                continue
            # Exclude hospital pharmacies or veterinary pharmacies if desired:
            if "hospital" in types or "veterinary_care" in types:
                continue

            # Deduplicate and record
            if pid not in pharmacies:
                loc = p["geometry"]["location"]
                pharmacies[pid] = {
                    "place_id": pid,
                    "name": name,
                    "latitude": loc["lat"],
                    "longitude": loc["lng"]
                }

    return list(pharmacies.values())

if __name__ == "__main__":
    all_pharmacies = collect_all_pharmacies()
    print(f"Total pharmacies found: {len(all_pharmacies)}")
    # Optionally save results to CSV
    import pandas as pd
    pd.DataFrame(all_pharmacies).to_csv("tbilisi_pharmacies.csv", index=False)
