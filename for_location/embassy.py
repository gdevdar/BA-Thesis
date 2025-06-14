import time
import math
import requests
from collections import deque
import pandas as pd

# ── CONFIG ─────────────────────────────────────────────────────────────────────

API_KEY        = "API_KEY"  # Replace with your real API key
SW_LAT, SW_LNG = 41.6100, 44.7000  # Southwest corner of Tbilisi
NE_LAT, NE_LNG = 41.8400, 44.9500  # Northeast corner of Tbilisi

INITIAL_RADIUS = 2000
MIN_RADIUS     = 500

# Different queries to increase coverage
SEARCH_CONFIGS = [
    {"type": "embassy", "keyword": ""},
    {"type": "embassy", "keyword": "embassy"},
    {"type": "embassy", "keyword": "consulate"},
    {"type": "embassy", "keyword": "foreign mission"},
    {"type": "establishment", "keyword": "embassy"},
    {"type": "establishment", "keyword": "consulate"},
]

# ── GRID SETUP ──────────────────────────────────────────────────────────────────

def generate_grid(sw_lat, sw_lng, ne_lat, ne_lng, radius):
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

def search_places(lat, lng, radius, place_type, keyword):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key": API_KEY,
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": place_type,
        "keyword": keyword
    }
    results = []
    while True:
        resp = requests.get(url, params=params).json()
        if resp.get("status") not in ["OK", "ZERO_RESULTS"]:
            print(f"Warning: {resp.get('status')} | type={place_type} | keyword={keyword}")
            break
        results.extend(resp.get("results", []))
        token = resp.get("next_page_token")
        if not token:
            break
        time.sleep(2)
        params = {"key": API_KEY, "pagetoken": token}
    return results

# ── MAIN DATA COLLECTION ───────────────────────────────────────────────────────

def collect_embassies():
    seen_ids = set()
    embassies = []
    grid = generate_grid(SW_LAT, SW_LNG, NE_LAT, NE_LNG, INITIAL_RADIUS)

    for config in SEARCH_CONFIGS:
        print(f"Searching: type={config['type']} | keyword={config['keyword']}")
        queue = deque(grid)
        while queue:
            lat, lng, rad = queue.popleft()
            results = search_places(lat, lng, rad, config["type"], config["keyword"])

            if len(results) >= 60 and rad > MIN_RADIUS:
                queue.extend(subdivide(lat, lng, rad))
                continue

            for place in results:
                pid = place["place_id"]
                if pid in seen_ids:
                    continue
                seen_ids.add(pid)

                name = place.get("name", "").lower()
                types = place.get("types", [])
                if "embassy" in name or "consulate" in name or "embassy" in types:
                    location = place["geometry"]["location"]
                    embassies.append({
                        "place_id": pid,
                        "name": place.get("name", ""),
                        "latitude": location["lat"],
                        "longitude": location["lng"],
                        "types": ",".join(types)
                    })

    return embassies

# ── RUN & EXPORT ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    embassies = collect_embassies()
    print(f"Total embassies found: {len(embassies)}")
    pd.DataFrame(embassies).to_csv("tbilisi_embassies.csv", index=False)
