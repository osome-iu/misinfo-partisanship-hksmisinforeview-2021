import os
import csv
import json
import numpy as np


def load_friends(filepath):
    with open(filepath, 'r') as f:
        friends_raw = json.loads(f.read())
    return {int(uid): set(friend_uids) for uid, friend_uids in friends_raw.items()}


def load_ideology(filepath):
    ideology = {}
    with open(filepath, 'r') as f:
        r = csv.reader(f, delimiter=',')
        next(r)
        for row in r:
            ideology[int(row[0])] = float(row[1])
    return ideology


def load_all_measures(filepath):
    with open(filepath, 'r') as f:
        return [row for row in csv.reader(f, delimiter='\t')]


def compute_ideology(twitter_uid, friends, ideology):
    scores = []
    if twitter_uid in friends:
        for fuid in friends[twitter_uid]:
            if fuid in ideology:
                scores.append(ideology[fuid])
    if len(scores) > 0:
        return np.average(scores)
    else:
        return None


def compute_ideologies(measures, friends, ideology_map):
    scores = {}
    for i in range(1, len(measures)):
        uid = int(measures[i][0])
        curr = compute_ideology(uid, friends, ideology_map)
        if curr is not None:
            scores[uid] = curr
    return scores


def compute_friends_ideology(uid, friends, ideologies):
    scores = []
    if uid in friends:
        for fuid in friends[uid]:
            if fuid in ideologies:
                scores.append(ideologies[fuid])
    if len(scores) > 0:
        return np.average(scores)
    else:
        return None

if __name__ == '__main__':
    print('Reading friends.')

    retweets = 'with-retweets'
    
    #ideology_map = load_ideology(os.path.join(os.getenv('D'), 'congress', 'final-ideology-map-senate.csv'))
    ideology_map = load_ideology(os.path.join(os.getenv('D'), 'congress', 'ideology-senate.csv'))
    measures = load_all_measures(os.path.join(os.getenv('D'), 'measures', retweets, 'partisanship.tab'))
    friends = load_friends(os.path.join(os.getenv('D'), 'friends.json'))
    
    ideologies = compute_ideologies(measures, friends, ideology_map)
    
    print('ideologies len: {}'.format(len(ideologies)))
    
    dest = os.path.join(os.getenv('D'), 'measures', retweets, 'ideology.tab')

    with open(dest, 'w') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(['Twitter ID', 'Ideology'])
        for i in range(1, len(measures)):
            row = measures[i]
            uid = int(row[0])
            if uid in ideologies:
                w.writerow([uid, ideologies[uid]])
                '''
                friends_ideology = compute_friends_ideology(uid, friends, ideologies)
                if friends_ideology is not None:
                    row.extend([ideologies[uid], friends_ideology])
                    w.writerow(row)
                '''
