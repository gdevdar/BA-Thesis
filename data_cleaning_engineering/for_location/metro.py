def grab_metro():
    place = "Tbilisi, Georgia"
    tags = {
        'station': 'subway'  # correct tag for metro stations
    }

    # Get the metro stations
    metro_stations = ox.features_from_place(place, tags)

    # Keep only name and geometry
    metro_stations = metro_stations[['name', 'geometry']].copy()

    # Step 1: Reproject to a metric CRS (e.g., UTM zone 38N for Tbilisi)
    metro_proj = metro_stations.to_crs(epsg=32638)

    # Step 2: Compute centroids safely in projected space
    metro_stations['geometry'] = metro_proj.centroid

    # Step 3: Reproject back to WGS84 to extract lat/lng
    metro_stations = metro_stations.to_crs(epsg=4326)

    # Extract latitude and longitude
    metro_stations['longitude'] = metro_stations.geometry.x
    metro_stations['latitude'] = metro_stations.geometry.y

    # Clean up
    metro_stations.reset_index(drop=True, inplace=True)
    result = metro_stations[['name', 'latitude', 'longitude']]

    # Save to CSV
    result.to_csv('for_location/metro_stations.csv', index=False)

def main():
    grab_metro()

import osmnx as ox

if __name__ == "__main__":
    main()