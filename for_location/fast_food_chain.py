import time
import math
import requests
from collections import deque
import pandas as pd

# ── CONFIG ─────────────────────────────────────────────────────────────────────

API_KEY        = "API_KEY"  # Replace with your actual API key
SW_LAT, SW_LNG = 41.6100, 44.7000
NE_LAT, NE_LNG = 41.8400, 44.9500

INITIAL_RADIUS = 2000
MIN_RADIUS     = 500
PLACE_TYPE     = "restaurant"

KEYWORDS = [
    "mcdonald", "mcdonalds",
    "wendy's", "wendys",
    "subway",
    "dunkin", "dunkin donuts", "dunkin' donuts",
    "kfc", "kentucky fried chicken",
    "domino", "domino's pizza"
]

# ── GRID ────────────────────────────────────────────────────────────────────────

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

def search_places(lat, lng, radius, keyword):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key": API_KEY,
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": PLACE_TYPE,
        "keyword": keyword
    }
    results = []
    while True:
        resp = requests.get(url, params=params).json()
        results.extend(resp.get("results", []))
        token = resp.get("next_page_token")
        if not token:
            break
        time.sleep(2)
        params = {"key": API_KEY, "pagetoken": token}
    return results

# ── COLLECTION LOOP ────────────────────────────────────────────────────────────

def collect_chain_for_keyword(keyword, seen_ids):
    queue = deque(generate_grid(SW_LAT, SW_LNG, NE_LAT, NE_LNG, INITIAL_RADIUS))
    places = []

    while queue:
        lat, lng, rad = queue.popleft()
        results = search_places(lat, lng, rad, keyword)

        if len(results) >= 60 and rad > MIN_RADIUS:
            queue.extend(subdivide(lat, lng, rad))
            continue

        for place in results:
            pid = place["place_id"]
            if pid in seen_ids:
                continue
            seen_ids.add(pid)
            name = place.get("name", "").lower()
            if keyword in name:
                location = place["geometry"]["location"]
                places.append({
                    "place_id": pid,
                    "name": place.get("name", ""),
                    "chain_keyword": keyword,
                    "latitude": location["lat"],
                    "longitude": location["lng"]
                })
    return places

# ── MAIN EXECUTION ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    all_places = []
    seen_ids = set()

    for kw in KEYWORDS:
        print(f"🔍 Searching for: {kw}")
        places = collect_chain_for_keyword(kw, seen_ids)
        print(f"✅ Found {len(places)} new places for '{kw}'")
        all_places.extend(places)

    print(f"\n🍟 Total unique fast food locations found: {len(all_places)}")
    df = pd.DataFrame(all_places)
    df.to_csv("tbilisi_fast_food_chain.csv", index=False)
