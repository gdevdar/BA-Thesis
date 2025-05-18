def true_ratio(row,boolean_columns):
    true_booleans = sum((row[col] is True) for col in boolean_columns if col in row)
    return true_booleans/len(boolean_columns)

def apply_true_ratio(df):
    boolean_columns = df.select_dtypes(include='bool').columns.tolist()
    df['true_ratio'] = df.apply(true_ratio, axis=1, boolean_columns=boolean_columns)
    return df
def engineer(df, reference_date):
    """
    user_id_count this shows basically how many apartments the user selling this house is selling at present.
    Will help us distinguish between big sellers and smaller sellers.

    """
    # Basically lets us see whether the user is a big seller or not
    #df['user_id_count'] = df['user_id'].map(df['user_id'].value_counts())

    # Dealing with date based variables
    reference_date = to_datetime(reference_date)
    # Creating created x days ago variable
    df['created_at'] = to_datetime(df['created_at'])
    df['created_days_ago'] = (reference_date - df['created_at']).dt.days + 1
    # Creating updated x days ago variable
    df['last_updated'] = to_datetime(df['last_updated'])
    df['updated_days_ago'] = (reference_date - df['last_updated']).dt.days + 1
    #df['has_project_id'] = df['project_id'].notna()
    #df['has_rs_code'] = df['rs_code'].notna()
    #df['vip'] = df[['is_vip', 'is_vip_plus', 'is_super_vip']].any(axis=1)

    # Dropping the variables used
    df = df.drop(['user_id','created_at', 'last_updated','project_id','rs_code','is_vip', 'is_vip_plus', 'is_super_vip'], axis=1)

    df = apply_true_ratio(df)
    return df

from pandas import to_datetime

def main():
    import pandas as pd
    df = pd.read_json('2025-05-02_eng.json')
    df = engineer(df,'2025-05-02')
if __name__ == "__main__":
    main()