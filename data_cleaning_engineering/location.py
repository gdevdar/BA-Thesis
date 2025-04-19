def extract_name_coord(raw_data):
    # Extract name and coordinates
    data = []
    for _, row in raw_data.iterrows():
        name = row.get('name', 'Unnamed')
        if row.geometry.geom_type == 'Point':
            lat, lon = row.geometry.y, row.geometry.x
        elif row.geometry.geom_type == 'Polygon':
            center = row.geometry.centroid
            lat, lon = center.y, center.x
        else:
            continue
        data.append((name, lat, lon))
    return data

def gather_data(tag_pairs):
    # Define the place you're interested in
    place_name = "Tbilisi, Georgia"
    df_collection = {}
    for tag in tag_pairs:
        tags = {tag_pairs[tag]: tag} # tags are used to search for the establishment
        raw_data = features_from_place(place_name, tags) # Here it searches in Tbilisi based on amenity
        raw_data = raw_data[raw_data.geometry.type.isin(['Point', 'Polygon'])] # This one filters the gathered data to only be points and polygons
        data = extract_name_coord(raw_data) # This one gathers the names and the coordinates
        df = DataFrame(data, columns=['Name', 'Latitude', 'Longitude']) # Then we convert it into a dataframe
        #df.to_csv(f"tbilisi_{tag}.csv", index=False) # Then we save it in CSV format
        #print(df.head())
        df_collection[tag] = df
    return df_collection
def measure_distance(latitude, longitude, category_df):
    df = category_df.copy()
    df['distance_km'] = haversine_distance(latitude, longitude, df['Latitude'],df['Longitude'])
    return df

def haversine_distance(lat1, lon1, lat2, lon2):
    r = 6371 # Earth radius in kilometers
    phi1 = radians(lat1)
    phi2 = radians(lat2)
    delta_phi = radians(lat2-lat1)
    delta_lambda = radians(lon2 - lon1)
    a = sin(delta_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2) ** 2
    c = 2 * arctan2(sqrt(a), sqrt(1 - a))
    return r*c

def near_5km(lat1,lon1,category_df):
    df = measure_distance(lat1, lon1, category_df)
    #print(df.shape[0])
    df = df[df['distance_km']<= 1]
    #print(df.shape[0])
    return df.shape[0]

def nearby_column_creator(main_df):
    tag_pairs = {'school':'amenity',
                 'pharmacy':'amenity',
                 'subway':'station',
                 'bus_stop':'highway',
                 'kindergarten':'amenity',
                 'atm':'amenity',
                 'payment_terminal': 'amenity',
                 'bank': 'amenity',
                 'clinic': 'amenity',
                 'marketplace': 'amenity',
                #'commercial': 'building',
                'fitness_centre':'leisure',
                'park':'leisure',
                'pitch':'leisure',
                'stadium':'leisure'
                }
    df_collection = gather_data(tag_pairs)
    for category in tag_pairs:
        main_df[f'near_{category}'] = main_df.apply(lambda row: near_5km(row['lng'], row['lat'], df_collection[category]), axis=1)

    return main_df


from osmnx import features_from_place
from pandas import DataFrame, read_csv
from numpy import radians, sin, cos,arctan2,sqrt
