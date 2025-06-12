import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree


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
        df = df.drop(columns=['30th_closest_km'])
    else:
        pass
    return df

def main():
    df = pd.read_json('new_2025-05-02.json')
    print(df.shape[0])
    df = location_clean_up(df)
    print(df.shape[0])
    #df2_sorted = df.sort_values(by='5th_closest_km', ascending=False)
    #print(df2_sorted['5th_closest_km'])
    #q95 = df2_sorted['5th_closest_km'].quantile(0.999)

    #print(f"95% quantile of 5th_closest_km: {q95:.2f} km")
if __name__ == "__main__":
    main()