# Request to gather images
# Collect requests in a list
# Use the hash method first. Convert responses to hashes, then compare hash distance
# If two of the rows are deemed to be different, then convert requests to the np array stuff
# Try the similarity code and then make the final decision
import requests
import pandas as pd

# The hashing method packages
import imagehash
from io import BytesIO
from PIL import Image

# For grayscale image method
import cv2
import numpy as np

import statistics

import time
from datetime import timedelta

import concurrent.futures

def initial_duplicates(df):
    return df.drop_duplicates(subset='id', keep='first')

def potential_duplicates(df):
    cols_to_check = ['lat', 'lng', 'floor', 'total_floors', 'area', 'room_type_id']
    duplicates =  df[df.duplicated(subset=cols_to_check, keep=False)].sort_values(by=cols_to_check).copy()
    duplicates['duplicate_group_id'] = duplicates.groupby(cols_to_check, sort=False).ngroup() + 1
    duplicates = duplicates[['id','images_large','duplicate_group_id']]
    return duplicates
# -----------------------------------------------------------------------------------------------
# Collecting images
def collect_link(url):
    fail_count  = 0
    while True:
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            return resp
        except Exception as e:
            #print(f"Error processing {url}: {e}")
            fail_count += 1
            if fail_count > 10:
                print(f"Completely failed {url}")
                return None

def cluster_collect(df_cluster):
    cluster_resp_list = []
    for link_list in df_cluster['images_large']:
        resp_list = [collect_link(u) for u in link_list]
        cluster_resp_list.append(resp_list)
    return cluster_resp_list
# -----------------------------------------------------------------------------------------------
# Hashes
def cluster_hash_collect(cluster_resp_list):
    cluster_hash_list = []
    for obs in cluster_resp_list:
        hash_list = []
        for resp in obs:
            try:
                img = Image.open(BytesIO(resp.content))
                hash_list.append(imagehash.phash(img))
            except Exception as e:
                print(f"We had this error: {Exception}")
        cluster_hash_list.append(hash_list)
    return cluster_hash_list

def hash_distance(list1, list2):
    if list1 and list2:
        hashes1 = list1
        hashes2 = list2
    else:
        return -1

    if len(hashes1) <= len(hashes2):
        smaller, larger = hashes1, hashes2
    else:
        smaller, larger = hashes2, hashes1

    for h1 in smaller: # The speed upgrade
        for h2 in larger:
            if h1-h2 < 10:
                return True
    return False
    #min_dists = [min(h1 - h2 for h2 in larger) for h1 in smaller]
    #median_min_distance = statistics.median(min_dists)
    #min_min_distance = min(min_dists)
    #return median_min_distance < 10
   # return min_min_distance<10
# -----------------------------------------------------------------------------------------------
# Gray scale image + stuff
def cluster_grayscale_collect(cluster_resp_list):
    cluster_grayscale_list = []
    for obs in cluster_resp_list:
        grayscale_list = []
        for resp in obs:
            try:
                data = np.frombuffer(resp.content, dtype=np.uint8)
                img = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)
                grayscale_list.append(img)
            except Exception as e:
                print(f"We had this error: {Exception}")
        cluster_grayscale_list.append(grayscale_list)
    return cluster_grayscale_list

def compare(imgs1,imgs2,orb, bf, ransac_thresh=5.0):

    imgs1 = [img for img in imgs1 if img is not None]
    imgs2 = [img for img in imgs2 if img is not None]

    # Treat both missing or all-invalid image cases as duplicates
    if not imgs1 or not imgs2:
        return True

    if len(imgs1) <= len(imgs2):
        smaller, larger = imgs1, imgs2
    else:
        smaller, larger = imgs2, imgs1

    max_inliers = 0

    # 2) For every pair of images, get keypoints/descriptors and match
    #inliers_list = []
    for imgA in smaller:
        max_inliers = 0
        kpA, desA = orb.detectAndCompute(imgA, None)
        if desA is None:
            continue
        for imgB in larger:
            kpB, desB = orb.detectAndCompute(imgB, None)
            if desB is None:
                continue

            matches = bf.match(desA, desB)
            if len(matches) < 8:
                continue

            # 3) RANSAC homography to count inliers
            ptsA = np.float32([kpA[m.queryIdx].pt for m in matches])
            ptsB = np.float32([kpB[m.trainIdx].pt for m in matches])
            H, mask = cv2.findHomography(ptsA, ptsB, cv2.RANSAC, ransac_thresh)

            if mask is not None:
                inliers = int(mask.sum())
                if inliers > 50: # Speed upgrade
                    return True
                #if inliers > max_inliers:
                    #max_inliers = inliers
        #inliers_list.append(max_inliers)
    #return max(inliers_list) > 50
    return False
    #return statistics.median(inliers_list) > 50
# -----------------------------------------------------------------------------------------------
# The main similarity check code
def batch_similarity(batch_df):
    batch_df.reset_index(drop=True, inplace=True)
    max_id = batch_df['duplicate_group_id'].max()
    min_id = batch_df['duplicate_group_id'].min()
    batch_df['similarity_id'] = pd.Series([pd.NA] * len(batch_df), dtype='Int64')
    batch_df['ghost_id'] = pd.Series([pd.NA] * len(batch_df), dtype='Int64')
    index = 0
    duplicate_index = 1
    ghost_index = 1
    _ORB = cv2.ORB_create(1000)
    _BF = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    threshold = 10
    start_time = time.time()
    for group in range(min_id, max_id + 1):
        #print(f'starting working on group {group} of {max_id-min_id+1}')
        generated = False
        df_cluster = batch_df[batch_df['duplicate_group_id'] == group].copy()
        cluster_len = df_cluster.shape[0]
        cluster_resp_list = cluster_collect(df_cluster)
        cluster_hash_list = cluster_hash_collect(cluster_resp_list)
        for i in range(cluster_len):
            dupe = False
            if i == 0:
                batch_df.loc[index,'similarity_id'] = duplicate_index
                batch_df.loc[index, 'ghost_id'] = ghost_index
            else:
                for j in range(i):
                    is_similar = hash_distance(cluster_hash_list[i],cluster_hash_list[j])
                    if is_similar:
                        batch_df.loc[index, 'similarity_id'] = batch_df.loc[index - i + j, 'similarity_id']
                        batch_df.loc[index, 'ghost_id'] = batch_df.loc[index - i + j, 'ghost_id']
                        dupe = True
                        break
                if not dupe:
                    ghost_index += 1
                    batch_df.loc[index, 'ghost_id'] = ghost_index
                    if not generated:
                        cluster_grayscale_list = cluster_grayscale_collect(cluster_resp_list)

                        generated = True
                    # Here write the same code but with the other function
                    for j in range(i):
                        is_similar = compare(cluster_grayscale_list[i],cluster_grayscale_list[j],_ORB,_BF)# The other function
                        if is_similar:
                            batch_df.loc[index, 'similarity_id'] = batch_df.loc[index - i + j, 'similarity_id']
                            dupe = True
                            break
                if not dupe:
                    duplicate_index += 1
                    batch_df.loc[index, 'similarity_id'] = duplicate_index
            index += 1
        duplicate_index += 1
        ghost_index += 1
        #end_time = time.time()
        #execution_time = end_time - start_time
        #formatted_time = str(timedelta(seconds=execution_time))
        #print(f'finished working on group {group} in {formatted_time}')
        completion_rate = (group - min_id + 1) / (max_id - min_id + 1) * 100
        if completion_rate > threshold:
            end_time = time.time()
            execution_time = end_time - start_time
            formatted_time = str(timedelta(seconds=execution_time))
            estimated_time = execution_time/threshold * (100-threshold)
            estimated_formatted_time = str(timedelta(seconds=estimated_time))
            print(f"Completed {threshold}% for batch {min_id}-{max_id} in {formatted_time}\nestimated time for completion: {estimated_formatted_time}")
            #start_time = time.time()
            threshold += 10
    print(f'completed batch {min_id}-{max_id} sir')
    return batch_df

# -----------------------------------------------------------------------------------------------
# Parallelizing the process
def batch_generate(df, num_of_batches = 16):
    num_clusters = int(df['duplicate_group_id'].max())
    step = num_clusters // num_of_batches
    boundaries = [round(step * i) for i in range(num_of_batches + 1)]
    boundaries[-1] = num_clusters
    boundaries[0] = 0
    batch_list = []
    for i in range(num_of_batches):
        df_batch = df[(df['duplicate_group_id']>boundaries[i])&(df['duplicate_group_id']<=boundaries[i+1])].copy()
        batch_list.append(df_batch.copy())
    return batch_list

def parallel_similarity(df):
    batch_list = batch_generate(df)
    workers = 8
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(batch_similarity , batch_list))
    combined_df=pd.concat(results, ignore_index=True)
    return combined_df

# -----------------------------------------------------------------------------------------------
# Cleaning the duplicates

def left_join(df1,df2):
    joint = pd.merge(df1,df2,on='id', how='left')
    return joint

def calculate_completeness(row, boolean_columns):
    # Count non-NA values
    non_na_count = row.notna().sum()

    # Count boolean False values as incomplete
    false_booleans = sum((row[col] is False) for col in boolean_columns if col in row)

    total_columns = len(row)
    completeness_score = (non_na_count - false_booleans) / total_columns
    return completeness_score

def apply_duplicates(df, df_dup):
    print(df.shape[0])
    merged = left_join(df, df_dup)
    max_existing_id = merged['duplicate_group_id'].max(skipna=True) or 0
    num_na = merged['duplicate_group_id'].isna().sum()
    new_ids = range(int(max_existing_id) + 1, int(max_existing_id) + 1 + num_na)
    merged.loc[merged['duplicate_group_id'].isna(), 'duplicate_group_id'] = new_ids
    merged['similarity_id'] = merged['similarity_id'].fillna(0)
    merged['group_uid'] = pd.factorize(pd.Series(list(zip(merged['duplicate_group_id'], merged['similarity_id']))))[0]
    boolean_columns = merged.select_dtypes(include='bool').columns.tolist()
    merged['completeness'] = merged.apply(calculate_completeness, axis=1, boolean_columns=boolean_columns)
    return merged
    #merged.to_json('play_data.json')
def remove_duplicates(df):
    #print(df['completeness'].mean())
    #print(df.shape[0])
    # 1) Create helper columns for easy sorting:
    df = df.copy()  # work on a copy to avoid SettingWithCopyWarning

    # Flag for physical users (True > False when sorting desc)
    df['is_physical'] = df['user_type'] == 'physical'

    # Flag for filled rs_code (True > False)
    df['has_rs_code'] = df['rs_code'].notna()

    # 2) Sort by group + your cascade of criteria:
    #    completeness (desc), is_physical (desc), has_rs_code (desc), user_statements_count (asc)
    df_sorted = df.sort_values(
        by=[
            'group_uid',
            'completeness',
            'is_physical',
            'has_rs_code',
            'user_statements_count'
        ],
        ascending=[
            True,  # keep group together
            False,  # highest completeness first
            False,  # True (physical) before False
            False,  # True (has code) before False
            True  # lowest statements count first
        ],
        na_position='last'  # in case completeness is NaN
    )

    # 3) Drop duplicates, keeping the “best” per group (the first in each group)
    deduped = df_sorted.drop_duplicates(
        subset='group_uid',
        keep='first'
    ).reset_index(drop=True)

    # (Optional) clean up helper columns
    deduped = deduped.drop(columns=['is_physical', 'has_rs_code'])
    #print(deduped['completeness'].mean())
    #print(deduped.shape[0])
    return deduped

def deduplicate(df):
    df = initial_duplicates(df)
    df_duplicate = potential_duplicates(df)
    df_duplicate = parallel_similarity(df_duplicate)
    df = apply_duplicates(df, df_duplicate)
    df = remove_duplicates(df)
    return df

def main():
    df = pd.read_json('2025-04-27.json')
    df = deduplicate(df)

if __name__ == "__main__":
    main()