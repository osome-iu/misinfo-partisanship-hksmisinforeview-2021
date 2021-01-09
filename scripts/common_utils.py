import os
import gzip
import json
import logging
import csv
import itertools
import numpy as np
from operator import itemgetter


def filter_dataset(data, keep_standalone=True, keep_retweet=True, keep_quote=True):
    new_data = {}
    skipped_counts = {
        'retweet': 0,
        'standalone': 0,
        'quote': 0
    }
    
    for raw_uid in data:
        uid = int(raw_uid)
        assert uid not in new_data
        new_data[uid] = []
        for tweet in data[raw_uid]:
            retweet = 'retweeted' in tweet
            quote = 'quoted' in tweet
            standalone = not retweet and not quote
            
            if standalone and not keep_standalone:
                skipped_counts['standalone'] += 1
                continue
            elif retweet and not keep_retweet:
                skipped_counts['retweet'] += 1
                continue
            elif quote and not keep_quote:
                skipped_counts['quote'] += 1
                continue

            new_data[uid].append(tweet)
    
    print('Skipped counts: {}'.format(skipped_counts))
    return new_data
        
def load_stripped_dataset(data_dir):
    users = {}
    for filepath in glob.glob(os.path.join(data_dir, '*.json')):
        with open(filepath, 'r') as f:
            d = json.loads(f.read())
            for raw_uid in d:
                uid = int(raw_uid)
                assert uid not in users
                users[uid] = d[raw_uid]
    return users


def load_bot_scores(filepath):
    with open(filepath, 'r') as f:
        r = csv.reader(f, delimiter=',')
        next(r)
        for row in r:
            uid = int(row[0])
            score = float(row[3])
            assert uid not in scores
            scores[uid] = score
    return scores


def gentweets(filepath):
    if filepath.endswith('.gz'):
        f = gzip.open(filepath, 'r')
    else:
        f = open(filepath, 'r')

    for line in f:
        if line.strip() != '':
            try:
                tweet = json.loads(line.strip())
            except:
                logging.info("Couldn't load tweet: %s", line)
                logging.info('Skipping.')
                continue
            yield tweet
    f.close()


def readcol(csv_filepath, col=0, delim='\t', skip_rows=0, apply_fn=None):
    if csv_filepath is None or not os.path.exists(csv_filepath):
        raise ValueError('Invalid filepath: {}.'.format(csv_filepath))

    items = []
    with open(csv_filepath, 'r') as f:
        reader = csv.reader(f, delimiter=delim)

        # skip header lines
        for _ in range(skip_rows):
            try:
                next(reader)
            except StopIteration:
                raise ValueError('Invalid skip_rows: {}, {}'.format(skip_rows, csv_filepath))

        for row in reader:
            if col >= len(row):
                raise ValueError('Invalid col: {}, {}'.format(col, csv_filepath))

            if apply_fn is not None:
                val = apply_fn(row[col])
            else:
                val = row[col]

            items.append(val)

    return items


def domain_count(domains, lookup_domains):
    '''
    >>> domain_count(frozenset(['google.com', 'nytimes.com', 'snopes.com']), frozenset(['snopes.com']))
    1
    >>> domain_count(['google.com', 'nytimes.com', 'snopes.com'], ['snopes.com'])
    1
    >>> domain_count({'google.com': 1, 'snopes.com': 5}, frozenset(['snopes.com']))
    5
    >>> domain_count({'google.com': 1, 'snopes.com': 5, 'politifact.com': 3}, frozenset(['snopes.com', 'politifact.com']))
    8
    >>> domain_count(frozenset(['snopes.com']), frozenset(['snopes.com']))
    1
    >>> domain_count(frozenset(['google.com']), frozenset(['snopes.com']))
    0
    >>> domain_count(frozenset(['google.com']), frozenset([]))
    0
    >>> domain_count(frozenset([]), frozenset(['snopes.com']))
    0
    >>> domain_count(frozenset([]), frozenset([]))
    0
    '''
    if not isinstance(lookup_domains, set) and not isinstance(lookup_domains, frozenset):
        lookup = frozenset(lookup_domains)
    else:
        lookup = lookup_domains

    if len(domains) == 0:
        return 0
    elif isinstance(domains, dict):
        return sum([count if d in lookup else 0 for d, count in domains.items()])
    else:
        return sum([1 if d in lookup else 0 for d in domains])


def reduce_collections(item_collections, reduce_fn, key_convert_fn=None, value_convert_fn=None, sort=False, reverse=False):
    d = {}
    for col in item_collections:
        # a collection can be a dict, or a set or list of tuples
        it = col.items() if isinstance(col, dict) else col
        for item in it:
            k = item[0] if key_convert_fn is None else key_convert_fn(item[0])
            v = item[1] if value_convert_fn is None else value_convert_fn(item[1])
            if k in d and reduce_fn is not None:
                d[k] = reduce_fn([d[k], v])
            elif k in d and reduce_fn is None:
                logging.debug('Alert! k is already in d. v = {}, d[k] = {}'.format(v, d[k]))
            else:
                d[k] = v
    if reverse:
        return sorted(d.items(), key=itemgetter(1), reverse=True)
    elif sort:
        return sorted(d.items(), key=itemgetter(1))
    else:
        return d.items()


def write_csv(filepath, items, headers=None, delimiter='\t'):
    with open(filepath, 'w') as f:
        w = csv.writer(f, delimiter=delimiter)
        if headers is not None:
            rows = [headers]
            rows.extend(items)
        else:
            rows = items
        w.writerows(rows)


def parts(lst, n, fill_value=None):
    '''
    Return the partitions of n elements of lst. The last partition is padded with fill_values.

    >>> list(parts(list(range(10)), 4))
    [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, None, None]]
    >>> list(parts(list(range(12)), 4))
    [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]]
    >>> list(parts([1, 2], 4))
    [[1, 2, None, None]]
    >>> list(parts([], 4))
    []
    '''
    for i in range(0, len(lst) - n + 1, n):
        yield lst[i:i+n]

    remaining = len(lst) % n
    if remaining != 0:
        yield lst[-remaining:] + [fill_value] * (n - remaining)


if __name__ == "__main__":
    logging.info('Testing...')
    import doctest
    doctest.testmod()

