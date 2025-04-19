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
        "data_update_count",
        "city_id",
        "city_name",
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
        "images_large",
        "images_blur",
        "images_thumb",
        "can_exchanged_comment"
    ]
    df = df.drop(useless_cols+price_cols+discussed_drop, axis=1)
    return df

def fill_na(df):
    # First let's deal with the numeric ones
    df['bedroom_type_id'] = df['bedroom_type_id'].fillna(0) # Check
    df['balconies'] = df['balconies'].fillna(0)
    df['balcony_area'] = df['balcony_area'].fillna(0)
    df['living_room_area'] = df['living_room_area'].fillna(0)
    df['porch_area'] = df['porch_area'].fillna(0)
    df['loggia_area'] = df['loggia_area'].fillna(0)
    df['storeroom_area'] = df['storeroom_area'].fillna(0)
    # Let's deal with the ids now
    df['condition_id'] = df['condition_id'].fillna(-1) # Maybe 0 is better.
    df['district_id'] = df['district_id'].fillna(-1)
    df['urban_id'] = df['urban_id'].fillna(-1)
    df['hot_water_type_id'] = df['hot_water_type_id'].fillna(-1)
    df['heating_type_id'] = df['heating_type_id'].fillna(-1)
    df['parking_type_id'] = df['parking_type_id'].fillna(-1)
    df['storeroom_type_id'] = df['storeroom_type_id'].fillna(-1)
    df['material_type_id'] = df['material_type_id'].fillna(-1)
    df['project_type_id'] = df['project_type_id'].fillna(-1)
    df['bathroom_type_id'] = df['bathroom_type_id'].fillna(-1)
    # Let's deal with text ones
    df['district_name'] = df['district_name'].fillna("-1")
    df['urban_name'] = df['urban_name'].fillna("-1")
    df['bathroom_type'] = df['bathroom_type'].fillna("-1")
    df['project_type'] = df['project_type'].fillna("-1")
    df['heating_type'] = df['heating_type'].fillna("-1")
    df['parking_type'] = df['parking_type'].fillna("-1")
    df['storeroom_type'] = df['storeroom_type'].fillna("-1")
    df['material_type'] = df['material_type'].fillna("-1")
    df['address'] = df['address'].fillna("-1")
    df['comment'] = df['comment'].fillna("-1")
    df['swimming_pool_type'] = df['swimming_pool_type'].fillna("-1")
    df['hot_water_type'] = df['hot_water_type'].fillna("-1")
    df['condition'] = df['condition'].fillna("-1")
    df['living_room_type'] = df['living_room_type'].fillna("-1")
    df['build_year'] = df['build_year'].fillna("-1")
    df['user_type'] = df['user_type'].fillna("-1")
    # Now unique cases
    df['has_project_id'] = df['project_id'].notna()
    df['has_rs_code'] = df['rs_code'].notna()
    df['rent_period_category'] = select( # Contact myhome.ge to figure out.
        [
            df['rent_period'].isna(),
            df['rent_period'] <50,
            df['rent_period'] >= 50
        ],
        [
            "-1",
            "low_rent_period",
            "high_rent_period"
        ],
        default =  '-1'
    )
    #df = df.drop(['rs_code','project_id','rent_period'], axis = 1)
    return df

def engineer(df, reference_date):
    """
    user_id_count this shows basically how many apartments the user selling this house is selling at present.
    Will help us distinguish between big sellers and smaller sellers.

    """
    # lat lng
    # comment
    # address
    # street_id
    # point_coordinates

    # Creating variable for user_id_count
    # Basically lets us see whether the user is a big seller or not
    df['user_id_count'] = df['user_id'].map(df['user_id'].value_counts())

    # Dealing with date based variables
    reference_date = to_datetime(reference_date)
    # Creating created x days ago variable
    df['created_at'] = to_datetime(df['created_at'])
    df['created_days_ago'] = (reference_date - df['created_at']).dt.days + 1
    # Creating updated x days ago variable
    df['last_updated'] = to_datetime(df['last_updated'])
    df['updated_days_ago'] = (reference_date - df['last_updated']).dt.days + 1


    # Dropping the variables used
    df = df.drop(['user_id','created_at', 'last_updated'], axis=1)
    return df

def full_transform(df, reference_date):
    return engineer(
        #fill_na(
            drop_useless(clean(df))
        #)
        ,reference_date)

from numpy import select
from pandas import to_datetime