def clean(df):
    """
    deal_type_id should always be 1 as that's the indicator that the house is sold and not rented or leased
    real_estate_type_id should be 1 as that means it's an apartment
    And rent_type_id shouldn't exist as the deal_type is selling
    Also dropping duplicates based on id, duplicates appear due to the nature of scraping
    """
    df = df[df["deal_type_id"] == 1]
    df = df[df["real_estate_type_id"] == 1]
    df = df[df["rent_type_id"].isna()]

    df = df.drop(["deal_type_id", "real_estate_type_id", "rent_type_id"], axis = 1)

    df = df.drop_duplicates(subset='id', keep='first')
    return df

def drop_useless(df):
    """
    The useless_cols list contains columns that either are always empty,
    or only take one value. Or have redundant information.
    The documentation for useless_cols is in the scraper documentation

    The idea of price_cols is to pick only one target variable.
    We also exclude price per square meter,
    as having area and price per square meter for a certain house may become a very powerful predictor.
    (It will result in leakage)

    The discussed drop:
    First I think YouTube link and those other links are useless
    Next the variables that show what is nearby are limited, and we want to engineer better variables ourselves
    And finally we have decided to not use images for now as they are out of scope for the thesis
    """
    useless_cols = [
        "appear_rs_code",
        "rent_period",
        "data_update_count",
        "city_id",
        "city_name",
        "published",
        "area_type_id",
        "is_owner",
        "is_active",
        "price_type_id",
        "has_asphalt_road",
        "can_be_divided_28",
        "with_building",
        "with_approved_project_30",
        "has_waiting_space",
        "has_cellar",
        "is_fenced",
        "has_gate",
        "has_fruit_trees",
        "has_yard_lighting",
        "has_yard",
        "for_party",
        "allows_pets",
        "with_approved_project_53",
        "can_be_divided_54",
        "owner_name",
        "user_phone_number",
        "rating",
        "gifts",
        "favorite",
        "price_negotiable",
        "price_from",
        "yard_area",
        "lease_period",
        "lease_type_id",
        "lease_type",
        "lease_contract_type_id",
        "daily_rent_type_id",
        "daily_rent_type",
        "waiting_space_area",
        "grouped_street_id",
        "price_label",
        "dynamic_title",
        "dynamic_slug",
        "additional_information"
    ]
    price_cols = [
        "price_1_price_total",
        "price_1_price_square",
        #"price_2_price_total", #Not dropping this, making this the target variable
        # "price_2_price_square",
        "price_3_price_total",
        "price_3_price_square",
        "total_price"
    ]

    discussed_drop = [
        "3d_url", # Useless
        "youtube_link", # Useless
        "airbnb_link", # Useless
        "booking_link", # Useless
        # These kinds of variables I think we should create instead
        "school_distance",
        "school_name",
        "school_lat",
        "school_lng",
        "miscellaneous_distance",
        "miscellaneous_name",
        "miscellaneous_lat",
        "miscellaneous_lng",
        "shop_distance",
        "shop_name",
        "shop_lat",
        "shop_lng",
        "fitness_distance",
        "fitness_name",
        "fitness_lat",
        "fitness_lng",
        "apothecary_distance",
        "apothecary_name",
        "apothecary_lat",
        "apothecary_lng",
        # We should create the distance from metro ourselves as well
        "metro_station", # We want to engineer such variables ourselves
        #"metro_station_id",

        "uuid", # Same as id but less useful
        "project_uuid", # Same as project_id which I turn into has_project id
        "currency_id", # Should have no impact
        # The pictures due to being out of scope for us
        "map_static_image",
        "all_nearby_places_image",
        #"images_large",
        "images_blur",
        "images_thumb",
        "can_exchanged_comment",
        "address",
        "comment",
        "point_coordinates",
        "street_id"
    ]

    duplicate_columns = [
        "condition_id",
        "status_id",
        "bathroom_type_id",
        "project_type_id",
        "hot_water_type_id",
        "heating_type_id",
        "parking_type_id",
        "storeroom_type_id",
        "material_type_id"
    ]
    redundant = [
        'living_room_area',
        'storeroom_area',
        'loggia_area',
        'porch_area',
        'balcony_area'
    ]
    to_drop = useless_cols+price_cols+discussed_drop+duplicate_columns+redundant

    df = df.drop(to_drop, axis=1)
    return df


from numpy import select
