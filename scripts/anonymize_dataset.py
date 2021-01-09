import os
import json
import random


if __name__ == '__main__':

    print('Reading shares.')
    with open(os.path.join(os.getenv('D'), 'stripped-dataset-no-bots.json'), 'r') as f:
        shares = json.loads(f.read())
    print('Num users: {}'.format(len(shares)))

    print('Reading friends.')
    with open(os.path.join(os.getenv('D'), 'friends-reduced.json'), 'r') as f:
        friends = json.loads(f.read())
    print('Num users: {}'.format(len(friends)))

    print('Creating list of ids.')
    uids = set([int(uid) for uid in friends.keys()]) | set([int(uid) for uid in shares.keys()])
    for uid in friends:
        for fuid in friends[uid]:
            if int(fuid) not in uids:
                uids.add(int(fuid))
    for uid in shares:
        for s in shares[uid]:
            if 'retweeted' in s:
                uids.add(int(s['retweeted']))
            elif 'quoted' in s:
                uids.add(int(s['quoted']))

    print('Creating mapping.')
    uids = list(uids)
    random.shuffle(uids)

    mapping = {}
    for i in range(len(uids)):
        mapping[uids[i]] = i+1
    print('Mappings: {}'.format(len(mapping)))

    print('Anonymizing tweets.')
    anon_shares = {}
    for uid in shares:
        anon_uid = mapping[int(uid)]
        anon_shares[anon_uid] = []
        
        for s in shares[uid]:
            new_s = {'domains': s['domains']}
            if 'retweeted' in s:
                new_s['retweeted'] = mapping[s['retweeted']]
            elif 'quoted' in s:
                new_s['quoted'] = mapping[s['quoted']]
            anon_shares[anon_uid].append(new_s)
    with open(os.path.join(os.getenv('D'), 'anonymized-shares.json'), 'w') as f:
        f.write(json.dumps(anon_shares))
    print('Num anon users with tweets: {}'.format(len(anon_shares)))

    print('Anonymizing friends.')
    anon_friends = {}
    for uid in friends:
        anon_uid = mapping[int(uid)]
        anon_friends[anon_uid] = set()
        for fuid in friends[uid]:
            anon_friends[anon_uid].add(mapping[fuid])
        anon_friends[anon_uid] = list(anon_friends[anon_uid])
    with open(os.path.join(os.getenv('D'), 'anonymized-friends.json'), 'w') as f:
        f.write(json.dumps(anon_friends))
    print('Num anon users with friends: {}'.format(len(anon_friends)))
    
