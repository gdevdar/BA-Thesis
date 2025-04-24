def fill_na(df):
    # First let's deal with the numeric ones
    df['bedroom_type_id'] = df['bedroom_type_id'].fillna(-1) # Check
    df['balconies'] = df['balconies'].fillna(-1)
    df['balcony_area'] = df['balcony_area'].fillna(-1)
    #df['living_room_area'] = df['living_room_area'].fillna(0)
    #df['porch_area'] = df['porch_area'].fillna(0)
    #df['loggia_area'] = df['loggia_area'].fillna(0)
    #df['storeroom_area'] = df['storeroom_area'].fillna(0)
    # Let's deal with the ids now
   # df['condition_id'] = df['condition_id'].fillna(-1) # Maybe 0 is better.
    #df['district_id'] = df['district_id'].fillna(-1)
    #df['urban_id'] = df['urban_id'].fillna(-1)
    #df['hot_water_type_id'] = df['hot_water_type_id'].fillna(-1)
    #df['heating_type_id'] = df['heating_type_id'].fillna(-1)
   # df['parking_type_id'] = df['parking_type_id'].fillna(-1)
   # df['storeroom_type_id'] = df['storeroom_type_id'].fillna(-1)
    #df['material_type_id'] = df['material_type_id'].fillna(-1)
    #df['project_type_id'] = df['project_type_id'].fillna(-1)
   # df['bathroom_type_id'] = df['bathroom_type_id'].fillna(-1)
    # Let's deal with text ones
    #df['district_name'] = df['district_name'].fillna("-1")
    #df['urban_name'] = df['urban_name'].fillna("-1")
    df['bathroom_type'] = df['bathroom_type'].fillna(-1)
    df['project_type'] = df['project_type'].fillna(-1)
    df['heating_type'] = df['heating_type'].fillna(-1)
    df['parking_type'] = df['parking_type'].fillna(-1)
    df['storeroom_type'] = df['storeroom_type'].fillna(-1)
    df['material_type'] = df['material_type'].fillna(-1)
    #df['address'] = df['address'].fillna("-1")
    #df['comment'] = df['comment'].fillna("-1")
    df['swimming_pool_type'] = df['swimming_pool_type'].fillna(-1)
    df['hot_water_type'] = df['hot_water_type'].fillna(-1)
    df['condition'] = df['condition'].fillna(-1)
    df['living_room_type'] = df['living_room_type'].fillna(-1)
    df['build_year'] = df['build_year'].fillna(-1)
    df['user_type'] = df['user_type'].fillna(-1)

    #df = df.drop(['rs_code','project_id','rent_period'], axis = 1)
    return df