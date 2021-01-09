import os
import json
import pprint
import csv
import re
from operator import itemgetter
from nltk.corpus import stopwords


def load_measure(filepath):
    measures = {}
    with open(filepath, 'r') as f:
        r = csv.reader(f, delimiter='\t')
        next(r) # skip header
        for row in r:
            uid = int(row[0])
            v = float(row[1])
            measures[uid] = v
    return measures


def load_shares(filepath):
    with open(filepath, 'r') as f:
        shares_raw = json.loads(f.read())
    return {int(uid): set(shares) for uid, shares in shares_raw.items()}


def load_friends(filepath):
    with open(filepath, 'r') as f:
        friends_raw = json.loads(f.read())
    return {int(uid): set(friend_uids) for uid, friend_uids in friends_raw.items()}


if __name__ == '__main__':
    partisanship = load_measure(os.path.join(os.getenv('D'), 'measures', 'with-retweets', 'partisanship.tab'))
    print(len(partisanship))

    friends = load_friends(os.path.join(os.getenv('D'), 'friends-reduced.json'))
    uids = set()
    for raw_uid in friends:
        uid = int(raw_uid)
        uids.add(uid)
        for raw_fuid in friends[raw_uid]:
            fuid = int(raw_fuid)
            uids.add(fuid)
    print(len(friends))
    print(len(uids))
