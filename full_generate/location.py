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

# def dist_to_metro(df):
#     metro_stations = pd.read_csv('for_location/metro_stations.csv')
#     df['nearest_metro_dist'] = df.progress_apply(lambda row: nearest_distance(row['lat'], row['lng'], metro_stations),
#         axis=1)
#     return df
    #print(df['nearest_metro_dist'].head())

def dist_to_center(df):
    cent_lat = 41.697007
    cent_lng = 44.799183
    df['city_center_dist'] = df.progress_apply(lambda row: haversine(row['lat'], row['lng'],cent_lat,cent_lng),axis=1)
    return df


def dist_to_places(df,path,name,df_coords):
    helper_table = pd.read_csv(path)
    coords = np.radians(helper_table[['latitude', 'longitude']].values)
    tree = BallTree(coords, metric='haversine')
    distances, _ = tree.query(df_coords, k=1)
    df[name] = distances[:, 0] * 6371
    return df

def dist_to_places_v1(df):
    bus_stops = pd.read_csv('for_location/tbilisi_bus_stops.csv')


    # Convert to radians for haversine
    stop_coords = np.radians(bus_stops[['latitude', 'longitude']].values)
    tree = BallTree(stop_coords, metric='haversine')  # uses haversine distance

    # Convert df points to radians
    df_coords = np.radians(df[['lat', 'lng']].values)

    # Query nearest neighbor
    distances, _ = tree.query(df_coords, k=1)  # distance in radians
    df['nearest_bus_stop_dist'] = distances[:, 0] * 6371  # convert to km

    return df

def create_location_features(df):
    df = dist_to_center(df)
    df_coords = np.radians(df[['lat', 'lng']].values)
    df = dist_to_places(df,'for_location/metro_stations.csv','nearest_metro_dist',df_coords)
    df = dist_to_places(df,'for_location/tbilisi_bus_stops.csv','nearest_bus_stop_dist',df_coords)
    df = dist_to_places(df, 'for_location/tbilisi_gyms.csv', 'nearest_gym_dist', df_coords)
    df = dist_to_places(df, 'for_location/tbilisi_kindergartens.csv', 'nearest_kindergarten_dist', df_coords)
    df = dist_to_places(df, 'for_location/tbilisi_parks.csv', 'nearest_park_dist', df_coords)
    df = dist_to_places(df, 'for_location/tbilisi_pharmacies.csv', 'nearest_pharmacy_dist', df_coords)
    df = dist_to_places(df, 'for_location/tbilisi_schools.csv', 'nearest_school_dist', df_coords)
    df = dist_to_places(df, 'for_location/tbilisi_supermarkets.csv', 'nearest_supermarket_dist', df_coords)
    df = dist_to_places(df, 'for_location/tbilisi_universities.csv', 'nearest_university_dist', df_coords)
    return df

def main():
    df = procedure('for_duplicate/duplicate_free.json')
    df = create_location_features(df)

from sklearn.neighbors import BallTree
from tqdm import tqdm
tqdm.pandas()
#import osmnx as ox
from procedure import procedure
from sklearn.neighbors import BallTree
import numpy as np
import pandas as pd

if __name__ == "__main__":
    main()