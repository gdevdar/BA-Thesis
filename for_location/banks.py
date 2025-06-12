import time
import math
import requests
from collections import deque

# ── CONFIG ─────────────────────────────────────────────────────────────────────

API_KEY        = "AIzaSyCr7JPiDAFQtDlHC7F8ByfoouowZCzLYnE"
SW_LAT, SW_LNG = 41.6100, 44.7000  # Southwest corner of Tbilisi
NE_LAT, NE_LNG = 41.8400, 44.9500  # Northeast corner of Tbilisi

INITIAL_RADIUS = 3000    # meters (larger tiles)
MIN_RADIUS     = 800     # meters (stop subdividing early)
PLACE_TYPE     = "bank"

# ── GRID SETUP ──────────────────────────────────────────────────────────────────

def generate_grid(sw_lat, sw_lng, ne_lat, ne_lng, radius):
    """Generate grid points covering the bounding box."""
    lat_step = (radius * 2) / 111000.0
    grid = []
    lat = sw_lat
    while lat <= ne_lat:
        lng_step = (radius * 2) / (111000.0 * math.cos(math.radians(lat)))
        lng = sw_lng
        while lng <= ne_lng:
            grid.append((lat, lng, radius))
            lng += lng_step
        lat += lat_step
    return grid

def subdivide(lat, lng, radius):
    """Split a search tile into 4 smaller tiles."""
    new_radius = radius / 2.0
    dlat = new_radius / 111000.0
    dlng = new_radius / (111000.0 * math.cos(math.radians(lat)))
    return [
        (lat + dlat, lng + dlng, new_radius),
        (lat + dlat, lng - dlng, new_radius),
        (lat - dlat, lng + dlng, new_radius),
        (lat - dlat, lng - dlng, new_radius)
    ]

# ── GOOGLE NEARBY SEARCH ───────────────────────────────────────────────────────

def search_banks(lat, lng, radius):
    """Nearby Search for banks around (lat, lng)."""
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key":      API_KEY,
        "location": f"{lat},{lng}",
        "radius":   radius,
        "type":     PLACE_TYPE
    }
    results = []
    while True:
        resp = requests.get(url, params=params).json()
        results.extend(resp.get("results", []))
        token = resp.get("next_page_token")
        if not token:
            break
        # wait for token activation
        time.sleep(2)
        params = {"key": API_KEY, "pagetoken": token}
    return results

# ── MAIN DATA COLLECTION ───────────────────────────────────────────────────────

def collect_banks():
    seen_ids = set()
    banks = []
    queue = deque(generate_grid(SW_LAT, SW_LNG, NE_LAT, NE_LNG, INITIAL_RADIUS))

    while queue:
        lat, lng, rad = queue.popleft()
        results = search_banks(lat, lng, rad)

        # if we hit the 60-result cap, subdivide further (down to MIN_RADIUS)
        if len(results) >= 60 and rad > MIN_RADIUS:
            queue.extend(subdivide(lat, lng, rad))
            continue

        for place in results:
            pid = place["place_id"]
            if pid in seen_ids:
                continue
            seen_ids.add(pid)

            if "bank" not in place.get("types", []):
                continue

            loc = place["geometry"]["location"]
            banks.append({
                "place_id": pid,
                "name":     place.get("name", ""),
                "latitude": loc["lat"],
                "longitude": loc["lng"]
            })

    return banks

# ── RUN & EXPORT ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    banks = collect_banks()
    print(f"Total banks found: {len(banks)}")

    # Save to CSV
    import pandas as pd
    pd.DataFrame(banks).to_csv("tbilisi_banks.csv", index=False)
