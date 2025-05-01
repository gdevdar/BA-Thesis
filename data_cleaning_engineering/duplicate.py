import pandas as pd
from imagehash import hex_to_hash
import statistics
import clean_data as cd
from na_fix import fill_na

import requests
from PIL import Image

from io import BytesIO
import imagehash

from tqdm import tqdm
import concurrent.futures

import numpy as np

# ---------------------------------------------------------------------------------------------
# stage 1
def get_image_hash(url):
    fail_count  = 0
    while True:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # raise exception for HTTP errors
            img = Image.open(BytesIO(response.content))
            # Compute the perceptual hash; you can switch to aHash or dHash if desired
            return imagehash.phash(img)
        except Exception as e:
            print(f"Error processing {url}: {e}")
            fail_count += 1
            if fail_count > 10:
                return None
def get_hashes(links):
    # Get perceptual hashes for each link as imagehash objects.
    #hashes = [get_image_hash(url) for url in links]
    #return [h for h in hashes if h is not None]
    hashes = [get_image_hash(url) for url in links if url]
    hashes = [h for h in hashes if h is not None]
    return sorted([str(h) for h in hashes if h is not None])

def initialize_df(path):
    tqdm.pandas()
    df = pd.read_json(path)
    df = cd.clean(df)
    print(df)
    #df = cd.drop_useless(cd.clean(df))
    #'2025-04-05'
    cols_to_check = ['lat', 'lng', 'floor', 'total_floors', 'area', 'room_type_id']
    df = df[df.duplicated(subset=cols_to_check, keep=False)].sort_values(by=cols_to_check)

    df_duplicates = df[df.duplicated(subset=cols_to_check, keep=False)].sort_values(by=cols_to_check).copy()

    # Assign a unique group id to each set of duplicates
    df_duplicates['duplicate_group_id'] = df_duplicates.groupby(cols_to_check, sort=False).ngroup() + 1

    df_duplicates = df_duplicates[['id','images_large','duplicate_group_id']]
    #df = df[['id', "images_large"]]
    return df_duplicates
def apply_get_hash(df):
    df['hash_list'] = df['images_large'].progress_apply(get_hashes)
    df = df[['id','hash_list','duplicate_group_id']]
    return df

def parallel_hash(df,num_workers):
    n_parts = num_workers * 3
    df_split = np.array_split(df, n_parts)
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        results = list(executor.map(apply_get_hash, df_split))
    combined_df = pd.concat(results, ignore_index=True)
    return combined_df

def generate_hash(path):
    #path = sys.argv[1]+".json"
    print(path)
    df = initialize_df(path)
    print(df)
    df = parallel_hash(df,num_workers = 8)
    df.to_json("for_duplicate/image_hash.json", orient="records", indent=2)

# ---------------------------------------------------------------------------------------------
# stage 2
def hash_distance(list1, list2):
    if list1 and list2:
        hashes1 = [hex_to_hash(h) for h in list1]
        hashes2 = [hex_to_hash(h) for h in list2]
    else:
        return -1

    if len(hashes1) <= len(hashes2):
        smaller, larger = hashes1, hashes2
    else:
        smaller, larger = hashes2, hashes1

    min_dists = [min(h1 - h2 for h2 in larger) for h1 in smaller]
    median_min_distance = statistics.median(min_dists)

    return median_min_distance

def check_duplicate():
    # Import the data
    hash_df = pd.read_json('for_duplicate/image_hash.json')
    # Calculating the number of clusters for the for loop
    num_clusters = hash_df['duplicate_group_id'].max()
    # Creating the new column which will give us info about the duplicates
    hash_df['true_duplicate_id'] = pd.Series([pd.NA] * len(hash_df), dtype='Int64')
    index = 0
    duplicate_index = 1
    for group in range(1,num_clusters+1):
        cluster_len = hash_df[hash_df['duplicate_group_id'] == group].shape[0]
        for i in range(cluster_len):
            dupe = False
            if i == 0:
                hash_df.loc[index,'true_duplicate_id'] = duplicate_index
            else:
                # Compare to previous i observations starting from the first
                for j in range(i):
                    distance = hash_distance(hash_df.loc[index,'hash_list'],hash_df.loc[index-i+j,'hash_list'])
                    if distance < 10:
                        hash_df.loc[index, 'true_duplicate_id'] = hash_df.loc[index-i+j,'true_duplicate_id']
                        dupe = True
                        break
                if not dupe:
                    duplicate_index += 1
                    hash_df.loc[index, 'true_duplicate_id'] = duplicate_index
            index += 1
        duplicate_index += 1
    df_duplicates = hash_df[['id','true_duplicate_id']]
    df_duplicates.to_json("for_duplicate/true_duplicates.json")

# ---------------------------------------------------------------------------------------------
# stage 3

def left_join(df1,df2):
    joint = pd.merge(df1,df2,on='id', how='left')
    return joint

def na_to_unique(df):
    # grabbing the highest existing duplicate_id
    max_existing_id = df['true_duplicate_id'].max(skipna=True) or 0
    num_na = df['true_duplicate_id'].isna().sum()
    new_ids = range(int(max_existing_id) + 1,int(max_existing_id) + 1 + num_na)
    df.loc[df['true_duplicate_id'].isna(), 'true_duplicate_id'] = new_ids
    df['true_duplicate_id'] = df['true_duplicate_id'].astype(int)
    return df

def deal_with_duplicate(path):
    true_duplicates = pd.read_json('for_duplicate/true_duplicates.json')
    main_df = pd.read_json(path)
    main_df = cd.clean(main_df)
    main_df = cd.drop_useless(main_df)
    main_df['completeness'] = main_df.notna().sum(axis=1)
    main_df['created_date'] = pd.to_datetime(main_df['created_at'])

    df = left_join(main_df,true_duplicates)
    df = na_to_unique(df)

    df_sorted = df.sort_values(
        by=['true_duplicate_id', 'completeness', 'created_date'],
        ascending=[True, False, True]
    )
    df = df_sorted.drop_duplicates(
        subset='true_duplicate_id',
        keep='first'
    ).reset_index(drop=True)
    df = df.drop(columns=['completeness','images_large','true_duplicate_id','created_date'])
    #df = df.drop_duplicates(subset='true_duplicate_id', keep='first')
    return df

# ---------------------------------------------------------------------------------------------
# full script

def full_procedure(path):
    generate_hash(path)
    check_duplicate()
    df = deal_with_duplicate(path)
    df.to_json("for_duplicate/duplicate_free.json")
def main():
    # full_procedure('05_04_2025.json','2025-04-05')
    full_procedure('2025-04-19.json')

if __name__ == "__main__":
    main()