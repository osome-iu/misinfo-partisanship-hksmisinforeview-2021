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


if __name__ == '__main__':
    keep_retweets = True
    base_dir = os.path.join(os.getenv('D'), 'measures', 'with-retweets' if keep_retweets else 'without-retweets')

    d1 = read_dataset(os.path.join(base_dir, 'partisanship.tab'))
    uids = set(d1.keys())
    with open(os.path.join(os.getenv('D'), 'uids.txt'), 'w') as f: 
        for uid in uids:
            f.write('{}\n'.format(uid))
    
