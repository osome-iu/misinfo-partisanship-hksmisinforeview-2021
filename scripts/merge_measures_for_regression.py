import os
import csv
import json
import logging
import math
from multiprocessing import Pool
from common_utils import gentweets
import numpy as np
from scipy import stats


def read_dataset(filepath, delim='\t', measure_col=1):
    dataset = {}
    with open(filepath, 'r') as f:
        reader = csv.reader(f, delimiter=delim)
        next(reader)
        for row in reader:
            uid = int(row[0])
            measure = float(row[measure_col])
            if measure != 0:
                dataset[uid] = measure
    return dataset


def normalize_dataset(dataset):
    #return scale_dataset(dataset)
    return zscore(dataset)


def zscore(dataset):
    uids = list(dataset.keys())
    vals = [dataset[u] for u in uids]
    zscores = stats.zscore(vals)
    new_dataset = {}
    for i in range(len(uids)):
        new_dataset[uids[i]] = zscores[i]
    return new_dataset


def scale_dataset(dataset):
    new_dataset = {}
    minv, maxv = min(dataset.values()), max(dataset.values())
    for uid in dataset:
        new_dataset[uid] = (dataset[uid] - minv) / (maxv - minv)
    return new_dataset


def left_dataset(dataset):
    new_dataset = {}
    for uid in dataset:
        if dataset[uid] < 0:
            new_dataset[uid] = abs(dataset[uid])
    return new_dataset


def right_dataset(dataset):
    new_dataset = {}
    for uid in dataset:
        if dataset[uid] > 0:
            new_dataset[uid] = dataset[uid]
    return new_dataset


def cohend(uids, dict1, dict2):
    uids = uids & set(dict1.keys()) & set(dict2.keys())
    d1, d2 = [], []
    for u in uids:
        d1.append(dict1[u])
        d2.append(dict2[u])
    d1 = np.array(d1)
    d2 = np.array(d2)
    
    # calculate the size of samples
    n1, n2 = len(d1), len(d2)
    # calculate the variance of the samples
    s1, s2 = np.var(d1, ddof=1), np.var(d2, ddof=1)
    # calculate the pooled standard deviation
    s = math.sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
    # calculate the means of the samples
    u1, u2 = np.mean(d1), np.mean(d2)
    # calculate the effect size
    return (u1 - u2) / s

if __name__ == '__main__':
    keep_retweets = True
    base_dir = os.path.join(os.getenv('D'), 'measures', 'with-retweets' if keep_retweets else 'without-retweets')

    partisanship = read_dataset(os.path.join(base_dir, 'partisanship.tab'))

    left_raw = left_dataset(partisanship)
    right_raw = right_dataset(partisanship)
    
    left_p = normalize_dataset(left_raw)
    right_p = normalize_dataset(right_raw)
    all_p = normalize_dataset(partisanship)

    pollution_raw = read_dataset(os.path.join(base_dir, 'pollution-filtered.tab'))
    pollution = normalize_dataset(pollution_raw)

    clustering_raw = read_dataset(os.path.join(base_dir, 'clustering.tab'))
    clustering = normalize_dataset(clustering_raw)

    tfidf_raw = read_dataset(os.path.join(base_dir, 'tfidf.tab'))
    tfidf = normalize_dataset(tfidf_raw)
    
    uids = set(partisanship.keys()) & set(pollution.keys()) & set(clustering.keys()) & set(tfidf.keys())

    print('Intersection: {}'.format(len(uids)))
    print('Partisanship: {}'.format(len(partisanship)))
    print('Pollution: {}'.format(len(pollution)))
    print('Clustering: {}'.format(len(clustering)))
    print('TF-IDF: {}'.format(len(tfidf)))

    left_uids = set(left_p.keys())
    right_uids = set(right_p.keys())

    print('Left')
    print('Length: {}'.format(len(left_uids)))
    print('partisanship: {}'.format(cohend(left_uids, left_raw, pollution_raw)))
    print('clustering: {}'.format(cohend(left_uids, pollution_raw, clustering_raw)))
    print('tfidf: {}'.format(cohend(left_uids, pollution_raw, tfidf_raw)))

    print('Right')
    print('Length: {}'.format(len(right_uids)))
    print('partisanship: {}'.format(cohend(right_uids, pollution_raw, right_raw)))
    print('clustering: {}'.format(cohend(right_uids, pollution_raw, clustering_raw)))
    print('tfidf: {}'.format(cohend(right_uids, pollution_raw, tfidf_raw)))
    
    f_all = open(os.path.join(base_dir, 'regression-all.tab'), 'w')
    f_left = open(os.path.join(base_dir, 'regression-left.tab'), 'w')
    f_right = open(os.path.join(base_dir, 'regression-right.tab'), 'w')

    w_all = csv.writer(f_all, delimiter='\t')
    w_left = csv.writer(f_left, delimiter='\t')
    w_right = csv.writer(f_right, delimiter='\t')

    header = ['Pollution', 'Partisanship', 'Clustering', 'TF-IDF']
    w_all.writerow(header)
    w_left.writerow(header)
    w_right.writerow(header)

    for uid in uids:
        w_all.writerow([pollution[uid], all_p[uid], clustering[uid], tfidf[uid]])
        if uid in left_p:
            w_left.writerow([pollution[uid], left_p[uid], clustering[uid], tfidf[uid]])
        elif uid in right_p:
            w_right.writerow([pollution[uid], right_p[uid], clustering[uid], tfidf[uid]])
        else:
            print('0 partisanship user.')
            
    f_all.close()
    f_left.close()
    f_right.close()
    
