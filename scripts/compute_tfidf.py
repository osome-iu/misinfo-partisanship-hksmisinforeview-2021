import os
import csv
import json
import math
import numpy as np
from operator import itemgetter
from common_utils import filter_dataset

def inverted_terms(shares):
    terms = {}
    for uid in shares:
        for share in shares[uid]:
            for d in share['domains']:
                if d not in terms:
                    terms[d] = set()
                terms[d].add(uid)
    return terms


def freqs(shares):
    domains = {}
    for s in shares:
        for d in s['domains']:
            if d not in domains:
                domains[d] = 0
            domains[d] += 1
    return domains


def compute_tfidf(shares, terms):
    N = len(shares)
    tfidf = {}
    for uid in shares:
        domain_freqs = freqs(shares[uid])
        if len(domain_freqs) == 0:
            continue
        elif uid not in tfidf:
            tfidf[uid] = {}

        max_freq = max(domain_freqs.values())
        for d, dfreq in domain_freqs.items():
            tf = .5 + .5 * (dfreq / max_freq)
            idf = math.log10(N / len(terms[d]))
            tfidf[uid][d] = tf * idf
    return tfidf


def compute_sim(u1, u2, tfidf):
    N1, N2 = len(tfidf[u1]), len(tfidf[u2])
    common_domains = set(tfidf[u1].keys()).intersection(set(tfidf[u2].keys()))
    return sum([tfidf[u1][d] * tfidf[u2][d] for d in common_domains]) / (N1 * N2)


def compute_tfidf_for_full_data(keep_retweets):
    suffix = 'with-retweets' if keep_retweets else 'without-retweets'
    shares_file = os.path.join(os.getenv('D'), 'stripped-dataset-no-bots.json')
    tfidf_file = os.path.join(os.getenv('D'), 'tfidf-{}.json'.format(suffix))

    print('Loading shares.')
    with open(shares_file, 'r') as f:
        shares = json.loads(f.read())
    print('Users: {}'.format(len(shares)))

    print('Removing retweets.')
    shares = filter_dataset(shares, keep_standalone=True, keep_retweet=keep_retweets, keep_quote=True)
    print('Users: {}'.format(len(shares)))

    print('Computing inverted index for terms.')
    terms = inverted_terms(shares)
    print('{} domains found.'.format(len(terms)))

    print('Computing tfidf')
    tfidf = compute_tfidf(shares, terms)
    with open(tfidf_file, 'w') as f:
        f.write(json.dumps(tfidf))

    print('Computing user similarities.')
    uids = sorted(shares.keys())
    sims = {}
    for i in range(len(uids)):
        u1 = uids[i]
        if u1 not in sims:
            sims[u1] = {}
            
        for j in range(len(uids)):
            u2 = uids[j]
            if u2 not in sims:
                sims[u2] = {}
                
            if i != j and u1 in tfidf and u2 in tfidf:
                if u1 in sims and u2 in sims[u1]:
                    sims[u2][u1] = sims[u1][u2]
                elif u2 in sims and u1 in sims[u2]:
                    sims[u1][u2] = sims[u2][u1]
                else:
                    s = compute_sim(u1, u2, tfidf)
                    sims[u1][u2] = s
                    sims[u2][u1] = s

    avg_sims = {u: np.average(list(sims[u].values())) for u in sims if len(sims[u]) > 0}
    with open(os.path.join(os.getenv('D'), 'average-cosine-tfidf-sim-{}.json'.format(suffix)), 'w') as f:
        f.write(json.dumps(avg_sims))


def temp():
    with open(os.path.join(os.getenv('D'), 'user-sim-tfidf.csv'), 'r') as f:
        r = csv.reader(f)
        next(r)
        sims = {}
        for u1, u2, sim in r:
            if sim != 0:
                if u1 not in sims:
                    sims[u1] = {}
                assert u2 not in sims[u1]
                sims[u1][u2] = sim

    with open(os.path.join(os.getenv('D'), 'user-sim-tfidf-new.csv'), 'w') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(['uid', 'similarities json'])
        for u1 in sims:
            w.writerow([u1, json.dumps(sims[u1])])
            

def to_csv(json_file, csv_file, header):
    with open(json_file, 'r') as f:
        js = json.loads(f.read())
    with open(csv_file, 'w') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(header)
        for k in js:
            w.writerow([int(k), float(js[k])])

    
def format_data(keep_retweets):
    suffix = 'with-retweets' if keep_retweets else 'without-retweets'
    to_csv(
        os.path.join(os.getenv('D'), 'average-cosine-tfidf-sim-{}.json'.format(suffix)),
        os.path.join(os.getenv('D'), 'measures', suffix, 'tfidf.tab'),
        ['Twitter ID', 'Average cosine sim']
    )

if __name__ == '__main__':
    keep_retweets = True
    compute_tfidf_for_full_data(keep_retweets)
    format_data(keep_retweets)
