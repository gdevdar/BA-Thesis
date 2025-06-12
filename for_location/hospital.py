import time
import math
import requests
from collections import deque

# ── CONFIG ─────────────────────────────────────────────────────────────────────

API_KEY        = "AIzaSyCr7JPiDAFQtDlHC7F8ByfoouowZCzLYnE"
SW_LAT, SW_LNG = 41.6100, 44.7000  # Southwest corner of Tbilisi
NE_LAT, NE_LNG = 41.8400, 44.9500  # Northeast corner of Tbilisi

INITIAL_RADIUS = 4000    # meters (very large tiles to minimize requests)
MIN_RADIUS     = 1000    # meters (stop subdividing once down to 1 km)
PLACE_TYPE     = "hospital"

# ── GRID SETUP ──────────────────────────────────────────────────────────────────

def generate_grid(sw_lat, sw_lng, ne_lat, ne_lng, radius):
    """Generate grid points to cover the bounding box."""
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

def search_hospitals(lat, lng, radius):
    """Nearby Search for hospitals around (lat, lng)."""
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
        # wait a couple seconds for the token to activate
        time.sleep(2)
        params = {"key": API_KEY, "pagetoken": token}
    return results

# ── MAIN DATA COLLECTION ───────────────────────────────────────────────────────

def collect_hospitals():
    seen_ids = set()
    hospitals = []
    queue = deque(generate_grid(SW_LAT, SW_LNG, NE_LAT, NE_LNG, INITIAL_RADIUS))

    while queue:
        lat, lng, rad = queue.popleft()
        results = search_hospitals(lat, lng, rad)

        # if we hit the 60-result cap, subdivide further (down to MIN_RADIUS)
        if len(results) >= 60 and rad > MIN_RADIUS:
            queue.extend(subdivide(lat, lng, rad))
            continue

        for place in results:
            pid = place["place_id"]
            if pid in seen_ids:
                continue
            seen_ids.add(pid)

            # ensure it's truly a hospital
            if "hospital" not in place.get("types", []):
                continue

            loc = place["geometry"]["location"]
            hospitals.append({
                "place_id": pid,
                "name":     place.get("name", ""),
                "latitude": loc["lat"],
                "longitude": loc["lng"]
            })

    return hospitals

# ── RUN & EXPORT ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    hospitals = collect_hospitals()
    print(f"Total hospitals found: {len(hospitals)}")

    # Save to CSV
    import pandas as pd
    pd.DataFrame(hospitals).to_csv("tbilisi_hospitals.csv", index=False)
