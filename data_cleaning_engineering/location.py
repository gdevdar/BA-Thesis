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
    return metro_stations[['name', 'latitude', 'longitude']]

def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert degrees to radians
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)

    # Haversine formula
    a = np.sin(delta_phi / 2.0) ** 2 + \
        np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0) ** 2
    c = 2 * np.arcsin(np.sqrt(a))

    return R * c  # distance in kilometers

def nearest_distance(lat, lng, dataframe):
    distances = dataframe.apply(
        lambda row: haversine(lat, lng, row['latitude'], row['longitude']), axis=1
    )
    return distances.min()

def dist_to_metro(df):
    metro_stations = grab_metro()
    df['nearest_metro_dist'] = df.apply(lambda row: nearest_distance(row['lat'], row['lng'], metro_stations),
        axis=1)
    return df
    #print(df['nearest_metro_dist'].head())

def dist_to_center(df):
    cent_lat = 41.697007
    cent_lng = 44.799183
    df['city_center_dist'] = df.apply(lambda row: haversine(row['lat'], row['lng'],cent_lat,cent_lng),axis=1)
    return df

def main():
    df = procedure('2025-04-19.json')
    df = dist_to_metro(df)
    df = dist_to_center(df)

import osmnx as ox
import numpy as np
from procedure import procedure

if __name__ == "__main__":
    main()