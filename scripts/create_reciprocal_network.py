import os
import json
from compute_congress_partisanship import load_friends

if __name__ == '__main__':
    dest = os.path.join(os.getenv('D'), 'friends-reciprocal.json')
    friends = load_friends(os.path.join(os.getenv('D'), 'friends.json'))
    new_friends = {}
    for uid, friend_uids in friends.items():
        for fuid in friend_uids:
            if fuid in friends and uid in friends[fuid]:
                if uid not in new_friends:
                    new_friends[uid] = set()
                if fuid not in new_friends:
                    new_friends[fuid] = set()
                new_friends[uid].add(fuid)
                new_friends[fuid].add(uid)
    for uid in new_friends:
        new_friends[uid] = list(new_friends[uid])
    with open(dest, 'w') as f:
        f.write(json.dumps(new_friends))
