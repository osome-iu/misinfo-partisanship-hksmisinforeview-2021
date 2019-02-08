'''
utils.py

Utility functions used by multiple scripts.
'''

import os
import gzip
import json
import logging
import csv
import itertools
import numpy as np
import string
from operator import itemgetter


def gen_shares(filepath):
    with open(filepath, 'r') as f:
        shares = json.loads(f.read())
        for uid in shares:
            for tid in shares[uid]:
                yield uid, tid, shares[uid][tid]


def domain(url):
    """
    >>> domain('http://https://test.com')
    'https'
    >>> domain('http://test.com?site=https://other.com')
    'test.com'
    >>> domain('http://test.com/index?test=1')
    'test.com'
    >>> domain('http://indiana.facebook.com/dir1/page.html')
    'indiana.facebook.com'
    >>> domain('http://facebook.com')
    'facebook.com'
    >>> domain('http://www.facebook.com:80/')
    'facebook.com'
    """
    url = (''.join(filter(lambda c: c in string.printable, url))).lower()

    # remove protocol
    idx = url.find("://")
    if idx != -1:
        url = url[idx + 3:]

    # remove port
    idx = url.find(":")
    if idx != -1:
        url = url[:idx]

    # remove trailing / and everything that follows
    idx = url.find("/")
    if idx != -1:
        url = url[:idx]

    # remove ? and anything that follows if it wasn't in previous steps
    idx = url.find("?")
    if idx != -1:
        url = url[:idx]

    url_is_clean = False
    while not url_is_clean:
        if url.startswith('www.'):
            url = url[4:]
        elif url.startswith('www2.') or url.startswith('www3.'):
            url = url[5:]
        else:
            url_is_clean = True
    return url


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


def write_csv(filepath, items, headers=None, delimiter='\t'):
    with open(filepath, 'w') as f:
        w = csv.writer(f, delimiter=delimiter)
        if headers is not None:
            rows = [headers]
            rows.extend(items)
        else:
            rows = items
        w.writerows(rows)


if __name__ == "__main__":
    logging.info('Testing...')
    import doctest
    doctest.testmod()

