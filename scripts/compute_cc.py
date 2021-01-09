import os
import json
import networkx as nx


def create_graph(friends_file):
    with open(friends_file, 'r') as f:
        friends = json.loads(f.read())

    G = nx.DiGraph()
    for raw_uid in friends:
        uid = int(raw_uid)
        for raw_fuid in friends[raw_uid]:
            fuid = int(raw_fuid)
            G.add_edge(uid, fuid)
    return G


if __name__ == '__main__':
    friends_file = os.path.join(os.getenv('D'), 'friends-reduced.json')

    print('Creating graph.')
    G = create_graph(friends_file)

    print('Computing cc.')
    cc = nx.clustering(G)

    print('Writing to file.')
    with open(os.path.join(os.getenv('D'), 'clustering.json'), 'w') as f:
        f.write(json.dumps(cc))
    
