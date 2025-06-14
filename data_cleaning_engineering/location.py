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

def dist_to_specific(df):
    # City Center
    cent_lat = 41.697007
    cent_lng = 44.799183
    df['city_center_dist'] = df.progress_apply(lambda row: haversine(row['lat'], row['lng'],cent_lat,cent_lng),axis=1)
    # Lisi Lake
    lisi_lat = 41.742885
    lisi_lng = 44.733691
    df['lisi_lake_dist'] = df.progress_apply(lambda row: haversine(row['lat'], row['lng'],lisi_lat,lisi_lng),axis=1)
    # Turtle Late
    ku_lat = 41.700945
    ku_lng = 44.754591
    df['ku_lake_dist'] = df.progress_apply(lambda row: haversine(row['lat'], row['lng'],ku_lat,ku_lng),axis=1)
    # Dinamo Stadium
    dinamo_lat = 41.722849
    dinamo_lng = 44.789828
    df['dinamo_dist'] = df.progress_apply(lambda row: haversine(row['lat'], row['lng'],dinamo_lat,dinamo_lng),axis=1)
    # Meskhi Stadium
    meskhi_lat = 41.710134
    meskhi_lng = 44.746094
    df['meskhi_dist'] = df.progress_apply(lambda row: haversine(row['lat'], row['lng'],meskhi_lat,meskhi_lng),axis=1)
    public_service_hall_lat = 41.699147
    public_service_hall_lng = 44.806558
    df['public_service_hall_dist'] = df.progress_apply(lambda row: haversine(row['lat'], row['lng'],public_service_hall_lat,public_service_hall_lng),axis=1)
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
    df = dist_to_specific(df)
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
    df = dist_to_places(df, 'for_location/tbilisi_atms.csv', 'nearest_atms_dist', df_coords)
    df = dist_to_places(df, 'for_location/tbilisi_banks.csv', 'nearest_banks_dist', df_coords)
    df = dist_to_places(df, 'for_location/tbilisi_gas_stations.csv', 'nearest_gas_dist', df_coords)
    df = dist_to_places(df, 'for_location/tbilisi_hospitals.csv', 'nearest_hospitals_dist', df_coords)
    df = dist_to_places(df, 'for_location/tbilisi_malls.csv', 'nearest_malls_dist', df_coords)
    # New
    df = dist_to_places(df, 'for_location/big_swimming_sites.csv', 'nearest_big_swimming_sites_dist', df_coords)
    df = dist_to_places(df, 'for_location/tbilisi_courts.csv', 'nearest_courts_dist', df_coords)
    df = dist_to_places(df, 'for_location/tbilisi_embassies.csv', 'nearest_embassies_dist', df_coords)
    df = dist_to_places(df, 'for_location/tbilisi_entertainment_venues.csv', 'nearest_entertainment_dist', df_coords)
    df = dist_to_places(df, 'for_location/tbilisi_fast_food_expanded.csv', 'nearest_fast_food_dist', df_coords)
    df = dist_to_places(df, 'for_location/tbilisi_police_stations.csv', 'nearest_police_stations_dist', df_coords)
    df = dist_to_places(df, 'for_location/tbilisi_swimming_pools.csv', 'nearest_swimming_pools_dist', df_coords)
    df = dist_to_places(df, 'for_location/tbilisi_fast_food_chain.csv', 'nearest_fast_food_chain_dist', df_coords)

    # 1 kilometer
    df = count_within_radius(df, 'for_location/metro_stations.csv', 'metro_stations_nearby_1km',df_coords,1)
    df = count_within_radius(df, 'for_location/tbilisi_bus_stops.csv', 'bus_stops_nearby_1km', df_coords, 1)
    df = count_within_radius(df, 'for_location/tbilisi_gyms.csv', 'gyms_nearby_1km', df_coords, 1)
    df = count_within_radius(df, 'for_location/tbilisi_kindergartens.csv', 'kindergartens_nearby_1km', df_coords, 1)
    df = count_within_radius(df, 'for_location/tbilisi_parks.csv', 'parks_nearby_1km', df_coords, 1)
    df = count_within_radius(df, 'for_location/tbilisi_pharmacies.csv', 'pharmacies_nearby_1km', df_coords, 1)
    df = count_within_radius(df, 'for_location/tbilisi_schools.csv', 'schools_nearby_1km', df_coords, 1)
    df = count_within_radius(df, 'for_location/tbilisi_supermarkets.csv', 'supermarkets_nearby_1km', df_coords, 1)
    df = count_within_radius(df, 'for_location/tbilisi_universities.csv', 'universities_nearby_1km', df_coords, 1)
    df = count_within_radius(df, 'for_location/tbilisi_atms.csv', 'atms_nearby_1km', df_coords, 1)
    df = count_within_radius(df, 'for_location/tbilisi_banks.csv', 'banks_nearby_1km', df_coords, 1)
    df = count_within_radius(df, 'for_location/tbilisi_gas_stations.csv', 'gas_stations_nearby_1km', df_coords, 1)
    df = count_within_radius(df, 'for_location/tbilisi_hospitals.csv', 'hospitals_nearby_1km', df_coords, 1)
    df = count_within_radius(df, 'for_location/tbilisi_malls.csv', 'malls_nearby_1km', df_coords, 1)
    #df = df.drop(columns=['lat','lng'])
    # new
    df = count_within_radius(df, 'for_location/big_swimming_sites.csv', 'big_swimming_sites_nearby_1km', df_coords,1)
    df = count_within_radius(df, 'for_location/tbilisi_courts.csv', 'courts_nearby_1km', df_coords,1)
    df = count_within_radius(df, 'for_location/tbilisi_embassies.csv', 'embassies_nearby_1km', df_coords,1)
    df = count_within_radius(df, 'for_location/tbilisi_entertainment_venues.csv', 'entertainment_nearby_1km', df_coords,1)
    df = count_within_radius(df, 'for_location/tbilisi_fast_food_expanded.csv', 'fast_food_nearby_1km', df_coords,1)
    df = count_within_radius(df, 'for_location/tbilisi_police_stations.csv', 'police_stations_nearby_1km', df_coords,1)
    df = count_within_radius(df, 'for_location/tbilisi_swimming_pools.csv', 'swimming_pools_nearby_1km', df_coords,1)
    df = count_within_radius(df, 'for_location/tbilisi_fast_food_chain.csv', 'fast_food_chain_nearby_1km', df_coords, 1)

    # 500 meters
    df = count_within_radius(df, 'for_location/metro_stations.csv', 'metro_stations_nearby_500m',df_coords,0.5)
    df = count_within_radius(df, 'for_location/tbilisi_bus_stops.csv', 'bus_stops_nearby_500m', df_coords, 0.5)
    df = count_within_radius(df, 'for_location/tbilisi_gyms.csv', 'gyms_nearby_500m', df_coords, 0.5)
    df = count_within_radius(df, 'for_location/tbilisi_kindergartens.csv', 'kindergartens_nearby_500m', df_coords, 0.5)
    df = count_within_radius(df, 'for_location/tbilisi_parks.csv', 'parks_nearby_500m', df_coords, 0.5)
    df = count_within_radius(df, 'for_location/tbilisi_pharmacies.csv', 'pharmacies_nearby_500m', df_coords,0.5)
    df = count_within_radius(df, 'for_location/tbilisi_schools.csv', 'schools_nearby_500m', df_coords,0.5)
    df = count_within_radius(df, 'for_location/tbilisi_supermarkets.csv', 'supermarkets_nearby_500m', df_coords,0.5)
    df = count_within_radius(df, 'for_location/tbilisi_universities.csv', 'universities_nearby_500m', df_coords,0.5)
    df = count_within_radius(df, 'for_location/tbilisi_atms.csv', 'atms_nearby_500m', df_coords,0.5)
    df = count_within_radius(df, 'for_location/tbilisi_banks.csv', 'banks_nearby_500m', df_coords,0.5)
    df = count_within_radius(df, 'for_location/tbilisi_gas_stations.csv', 'gas_stations_nearby_500m', df_coords, 0.5)
    df = count_within_radius(df, 'for_location/tbilisi_hospitals.csv', 'hospitals_nearby_500m', df_coords,0.5)
    df = count_within_radius(df, 'for_location/tbilisi_malls.csv', 'malls_nearby_500m', df_coords,0.5)
    # new
    df = count_within_radius(df, 'for_location/big_swimming_sites.csv', 'big_swimming_sites_nearby_500m', df_coords,0.5)
    df = count_within_radius(df, 'for_location/tbilisi_courts.csv', 'courts_nearby_500m', df_coords,0.5)
    df = count_within_radius(df, 'for_location/tbilisi_embassies.csv', 'embassies_nearby_500m', df_coords,0.5)
    df = count_within_radius(df, 'for_location/tbilisi_entertainment_venues.csv', 'entertainment_nearby_500m', df_coords,0.5)
    df = count_within_radius(df, 'for_location/tbilisi_fast_food_expanded.csv', 'fast_food_nearby_500m', df_coords,0.5)
    df = count_within_radius(df, 'for_location/tbilisi_police_stations.csv', 'police_stations_nearby_500m', df_coords,0.5)
    df = count_within_radius(df, 'for_location/tbilisi_swimming_pools.csv', 'swimming_pools_nearby_500m', df_coords,0.5)
    df = count_within_radius(df, 'for_location/tbilisi_fast_food_chain.csv', 'fast_food_chain_nearby_500m', df_coords, 0.5)

    # 200 meters
    df = count_within_radius(df, 'for_location/metro_stations.csv', 'metro_stations_nearby_200m',df_coords,0.2)
    df = count_within_radius(df, 'for_location/tbilisi_bus_stops.csv', 'bus_stops_nearby_200m', df_coords, 0.2)
    df = count_within_radius(df, 'for_location/tbilisi_gyms.csv', 'gyms_nearby_200m', df_coords, 0.2)
    df = count_within_radius(df, 'for_location/tbilisi_kindergartens.csv', 'kindergartens_nearby_200m', df_coords, 0.2)
    df = count_within_radius(df, 'for_location/tbilisi_parks.csv', 'parks_nearby_200m', df_coords, 0.2)
    df = count_within_radius(df, 'for_location/tbilisi_pharmacies.csv', 'pharmacies_nearby_200m', df_coords,0.2)
    df = count_within_radius(df, 'for_location/tbilisi_schools.csv', 'schools_nearby_200m', df_coords,0.2)
    df = count_within_radius(df, 'for_location/tbilisi_supermarkets.csv', 'supermarkets_nearby_200m', df_coords,0.2)
    df = count_within_radius(df, 'for_location/tbilisi_universities.csv', 'universities_nearby_200m', df_coords,0.2)
    df = count_within_radius(df, 'for_location/tbilisi_atms.csv', 'atms_nearby_200m', df_coords,0.2)
    df = count_within_radius(df, 'for_location/tbilisi_banks.csv', 'banks_nearby_200m', df_coords,0.2)
    df = count_within_radius(df, 'for_location/tbilisi_gas_stations.csv', 'gas_stations_nearby_200m', df_coords, 0.2)
    df = count_within_radius(df, 'for_location/tbilisi_hospitals.csv', 'hospitals_nearby_200m', df_coords,0.2)
    df = count_within_radius(df, 'for_location/tbilisi_malls.csv', 'malls_nearby_200m', df_coords,0.2)
    # new
    df = count_within_radius(df, 'for_location/big_swimming_sites.csv', 'big_swimming_sites_nearby_200m', df_coords,0.2)
    df = count_within_radius(df, 'for_location/tbilisi_courts.csv', 'courts_nearby_200m', df_coords,0.2)
    df = count_within_radius(df, 'for_location/tbilisi_embassies.csv', 'embassies_nearby_200m', df_coords,0.2)
    df = count_within_radius(df, 'for_location/tbilisi_entertainment_venues.csv', 'entertainment_nearby_200m', df_coords,0.2)
    df = count_within_radius(df, 'for_location/tbilisi_fast_food_expanded.csv', 'fast_food_nearby_200m', df_coords,0.2)
    df = count_within_radius(df, 'for_location/tbilisi_police_stations.csv', 'police_stations_nearby_200m', df_coords,0.2)
    df = count_within_radius(df, 'for_location/tbilisi_swimming_pools.csv', 'swimming_pools_nearby_200m', df_coords,0.2)
    df = count_within_radius(df, 'for_location/tbilisi_fast_food_chain.csv', 'fast_food_chain_nearby_200m', df_coords, 0.2)

    # 100 meters
    df = count_within_radius(df, 'for_location/metro_stations.csv', 'metro_stations_nearby_100m',df_coords,0.1)
    df = count_within_radius(df, 'for_location/tbilisi_bus_stops.csv', 'bus_stops_nearby_100m', df_coords, 0.1)
    df = count_within_radius(df, 'for_location/tbilisi_gyms.csv', 'gyms_nearby_100m', df_coords, 0.1)
    df = count_within_radius(df, 'for_location/tbilisi_kindergartens.csv', 'kindergartens_nearby_100m', df_coords, 0.1)
    df = count_within_radius(df, 'for_location/tbilisi_parks.csv', 'parks_nearby_100m', df_coords, 0.1)
    df = count_within_radius(df, 'for_location/tbilisi_pharmacies.csv', 'pharmacies_nearby_100m', df_coords,0.1)
    df = count_within_radius(df, 'for_location/tbilisi_schools.csv', 'schools_nearby_200m', df_coords,0.1)
    df = count_within_radius(df, 'for_location/tbilisi_supermarkets.csv', 'supermarkets_nearby_100m', df_coords,0.1)
    df = count_within_radius(df, 'for_location/tbilisi_universities.csv', 'universities_nearby_100m', df_coords,0.1)
    df = count_within_radius(df, 'for_location/tbilisi_atms.csv', 'atms_nearby_100m', df_coords,0.1)
    df = count_within_radius(df, 'for_location/tbilisi_banks.csv', 'banks_nearby_100m', df_coords,0.1)
    df = count_within_radius(df, 'for_location/tbilisi_gas_stations.csv', 'gas_stations_nearby_100m', df_coords, 0.1)
    df = count_within_radius(df, 'for_location/tbilisi_hospitals.csv', 'hospitals_nearby_100m', df_coords,0.1)
    df = count_within_radius(df, 'for_location/tbilisi_malls.csv', 'malls_nearby_100m', df_coords,0.1)
    # new
    df = count_within_radius(df, 'for_location/big_swimming_sites.csv', 'big_swimming_sites_nearby_100m', df_coords,0.1)
    df = count_within_radius(df, 'for_location/tbilisi_courts.csv', 'courts_nearby_100m', df_coords,0.1)
    df = count_within_radius(df, 'for_location/tbilisi_embassies.csv', 'embassies_nearby_100m', df_coords,0.1)
    df = count_within_radius(df, 'for_location/tbilisi_entertainment_venues.csv', 'entertainment_nearby_100m', df_coords,0.1)
    df = count_within_radius(df, 'for_location/tbilisi_fast_food_expanded.csv', 'fast_food_nearby_100m', df_coords,0.1)
    df = count_within_radius(df, 'for_location/tbilisi_police_stations.csv', 'police_stations_nearby_100m', df_coords,0.1)
    df = count_within_radius(df, 'for_location/tbilisi_swimming_pools.csv', 'swimming_pools_nearby_100m', df_coords,0.1)
    df = count_within_radius(df, 'for_location/tbilisi_fast_food_chain.csv', 'fast_food_chain_nearby_100m', df_coords, 0.1)

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
    #print("The shape of the df is",df.shape[0])
    if df.shape[0] > 31:
        df = add_30th_closest(df)
        df = df[df['30th_closest_km'] <= 2]
        df = df.drop(columns = ['30th_closest_km'])
    else:
        pass
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