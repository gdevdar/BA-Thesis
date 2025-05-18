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

def count_within_radius(df, path, name, df_coords, radius_km):
    est_df = pd.read_csv(path)
    est_coords = np.radians(est_df[['latitude','longitude']].values)
    earth_radius_km = 6371.0
    tree = BallTree(est_coords, metric='haversine')
    radius_rad = radius_km / earth_radius_km
    counts = tree.query_radius(df_coords, r=radius_rad, count_only=True)
    result_df = df.copy()
    result_df[name] = counts
    return result_df

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

    df = count_within_radius(df, 'for_location/metro_stations.csv', 'metro_stations_nearby',df_coords,1)
    df = count_within_radius(df, 'for_location/tbilisi_bus_stops.csv', 'bus_stops_nearby', df_coords, 1)
    df = count_within_radius(df, 'for_location/tbilisi_gyms.csv', 'gyms_nearby', df_coords, 1)
    df = count_within_radius(df, 'for_location/tbilisi_kindergartens.csv', 'kindergartens_nearby', df_coords, 1)
    df = count_within_radius(df, 'for_location/tbilisi_parks.csv', 'parks_nearby', df_coords, 1)
    df = count_within_radius(df, 'for_location/tbilisi_pharmacies.csv', 'pharmacies_nearby', df_coords, 1)
    df = count_within_radius(df, 'for_location/tbilisi_schools.csv', 'schools_nearby', df_coords, 1)
    df = count_within_radius(df, 'for_location/tbilisi_supermarkets.csv', 'supermarkets_nearby', df_coords, 1)
    df = count_within_radius(df, 'for_location/tbilisi_universities.csv', 'universities_nearby', df_coords, 1)

    #df = df.drop(columns=['lat','lng'])
    return df

def add_30th_closest(df, earth_radius_km=6371):
    """
    Given a DataFrame with columns ['lat','lng','urban'],
    returns a copy with a new column '5th_closest_km'.
    """

    def compute_group(g):
        if len(g) < 6:
            # not enough points → fill with NaN
            g['5th_closest_km'] = np.nan
            return g

        # convert degrees to radians for haversine
        coords = np.deg2rad(g[['lat', 'lng']].to_numpy())

        # build BallTree with haversine metric
        tree = BallTree(coords, metric='haversine')

        # query 6 neighbors (including self at index 0)
        dists, idxs = tree.query(coords, k=31)

        # the 6th neighbor → index 5 in zero-based Python
        # multiply by earth_radius → distance in km
        g['30th_closest_km'] = dists[:, 30] * earth_radius_km
        return g

    df2 = (
        df
        .groupby('urban', group_keys=False)
        .apply(compute_group)
    )
    # apply group-wise
    #df.groupby('urban', group_keys=False).apply(compute_group)
    return df2

def location_clean_up(df):
    df = add_30th_closest(df)
    df = df[df['30th_closest_km'] <= 2]
    df = df.drop(columns = ['30th_closest_km'])
    return df


def main():
    #df = procedure('for_duplicate/duplicate_free.json')
    import pandas as pd
    df = pd.read_json('2025-05-02.json')
    df = df.iloc[:1000]
    df = create_location_features(df)
    print(df[["price_2_price_square",'metro_stations_nearby','bus_stops_nearby','gyms_nearby','kindergartens_nearby'
              ,'parks_nearby','pharmacies_nearby', 'schools_nearby','supermarkets_nearby','universities_nearby']].corr())
from sklearn.neighbors import BallTree
import numpy as np
import pandas as pd

from tqdm import tqdm
tqdm.pandas()
import osmnx as ox
#from procedure import procedure
from sklearn.neighbors import BallTree
import numpy as np
import pandas as pd

if __name__ == "__main__":
    main()