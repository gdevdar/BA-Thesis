import time
import math
import requests
from collections import deque

# ── CONFIG ─────────────────────────────────────────────────────────────────────

API_KEY        = "AIzaSyCr7JPiDAFQtDlHC7F8ByfoouowZCzLYnE"
SW_LAT, SW_LNG = 41.6100, 44.7000  # Southwest corner of Tbilisi
NE_LAT, NE_LNG = 41.8400, 44.9500  # Northeast corner of Tbilisi

INITIAL_RADIUS = 1000    # meters
MIN_RADIUS     = 200     # meters
PLACE_TYPE     = "atm"   # collect ATMs

# ── GRID SETUP ──────────────────────────────────────────────────────────────────

def generate_grid(sw_lat, sw_lng, ne_lat, ne_lng, radius):
    """Generate grid points with radius to cover entire Tbilisi area."""
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
    """Divide a search region into 4 smaller parts for higher resolution."""
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

def search_atms(lat, lng, radius):
    """Perform a Nearby Search for ATMs around (lat, lng)."""
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key": API_KEY,
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": PLACE_TYPE
    }
    results = []
    while True:
        resp = requests.get(url, params=params).json()
        results.extend(resp.get("results", []))
        token = resp.get("next_page_token")
        if not token:
            break
        # next_page_token may take a couple seconds to activate
        time.sleep(2)
        params = {"key": API_KEY, "pagetoken": token}
    return results

# ── MAIN DATA COLLECTION ───────────────────────────────────────────────────────

def collect_atms():
    seen_ids = set()
    atms = []
    queue = deque(generate_grid(SW_LAT, SW_LNG, NE_LAT, NE_LNG, INITIAL_RADIUS))

    while queue:
        lat, lng, rad = queue.popleft()
        results = search_atms(lat, lng, rad)

        # if the area is dense (max 60 results returned) subdivide further
        if len(results) >= 60 and rad > MIN_RADIUS:
            queue.extend(subdivide(lat, lng, rad))
            continue

        for place in results:
            pid = place["place_id"]
            if pid in seen_ids:
                continue
            seen_ids.add(pid)

            types = place.get("types", [])
            # filter to ensure it's actually an ATM
            if "atm" not in types:
                continue

            location = place["geometry"]["location"]
            atms.append({
                "place_id": pid,
                "name": place.get("name", ""),
                "latitude": location["lat"],
                "longitude": location["lng"]
            })

    return atms

# ── RUN & EXPORT ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    atms = collect_atms()
    print(f"Total ATMs found: {len(atms)}")

    # Save to CSV
    import pandas as pd
    pd.DataFrame(atms).to_csv("tbilisi_atms.csv", index=False)
