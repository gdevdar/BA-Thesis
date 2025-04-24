def coordinate_swap(df):
    df['lat'], df['lng'] = df['lng'], df['lat']
    return df

def create_condition(df):
    lat_min, lat_max = 41.625325, 41.838071
    lng_min, lng_max = 44.595510, 45.017821
    condition = ~df['lat'].between(lat_min, lat_max) | ~df['lng'].between(lng_min, lng_max)
    return condition

def conditional_swap(df,condition):
    df.loc[condition, ['lat', 'lng']] = df.loc[condition, ['lng', 'lat']].values
    return df

def drop_outliers(df,condition):
    # Drop rows that match the invalid condition
    df = df[~condition].reset_index(drop=True)
    return df

def coordinate_fix(df):
    df = coordinate_swap(df)
    condition = create_condition(df)
    df = conditional_swap(df,condition)
    df = drop_outliers(df,condition)
    return df
