import os
import csv
import logging
from multiprocessing import Pool
from utils import readcol, gentweets, write_csv
from urls import domain

logging.basicConfig(level=logging.DEBUG)


def compute_misinfo_bias(filepath, misinfo_sites, min_num_tweets):
    logging.debug('Processing {}, {}, {}'.format(filepath, len(misinfo_sites), min_num_tweets))

    total_counts = {}
    misinfo_counts = {}
    for tweet in gentweets(filepath):
        uid = tweet['user']['id']
        if uid not in total_counts:
            total_counts[uid] = 0
        if uid not in misinfo_counts:
            misinfo_counts[uid] = 0

        if 'entities' in tweet and 'urls' in tweet['entities']:
            for raw_url in tweet['entities']['urls']:
                if raw_url['expanded_url'] is not None:
                    total_counts[uid] += 1
                    url = domain(raw_url['expanded_url'])
                    if url in misinfo_sites:
                        misinfo_counts[uid] += 1

    scores = {}
    for uid in misinfo_counts:
        if total_counts[uid] < min_num_tweets:
            logging.info('User {} does not have the required minimum number of tweets ({}/{}). Skipping.'.format(
                uid, total_counts[uid], min_num_tweets
            ))
            continue
        else:
            scores[uid] = misinfo_counts[uid] / total_counts[uid]
    return scores


def mapper(args):
    return compute_misinfo_bias(*args)


if __name__ == '__main__':
    tweets_dir = os.path.join(os.getenv('D'), 'indexed-tweets', 'with-misinfo')
    dest = os.path.join(os.getenv('D'), 'measures', 'over-all-tweets', 'misinfo', 'with-misinfo.tab')

    misinfo_sites = frozenset(readcol(os.path.join(os.getenv('D'), 'sources', 'misinfo.tab'), skip_rows=1))
    params = [(os.path.join(tweets_dir, f), misinfo_sites, 10) for f in os.listdir(tweets_dir)]

    pool = Pool(processes=10)
    results = pool.map(mapper, params)

    scores = []
    for r in results:
        scores.extend(r.items())

    if not os.path.exists(os.path.dirname(dest)):
        os.makedirs(os.path.dirname(dest))
    write_csv(dest, scores, ['Twitter ID', 'Misinformation Bias'])
