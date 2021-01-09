import os
import json
import logging
import argparse
import glob
from multiprocessing import Pool
import lib.config as config
from lib.urls import domain
from lib.common import gentweets

logging.basicConfig(level=config.DEBUG_LEVEL)


def extract_data(tweet):
    domains = set()
    if 'entities' in tweet and 'urls' in tweet['entities'] and len(tweet['entities']['urls']) > 0:
        for url in tweet['entities']['urls']:
            if url['expanded_url'] is not None:
                domains.add(domain(url['expanded_url']))
    uid = tweet['user']['id']
    return uid, domains


def mapper(args):
    return strip_tweets(*args)


def strip_tweets(src_filepath, dest_filepath):
    logging.info('Stripping tweets into %s.', dest_filepath)

    src_basename = os.path.splitext(os.path.basename(src_filepath))[0]
    dest_basename = os.path.splitext(os.path.basename(dest_filepath))[0]
    assert src_basename == dest_basename
    
    data = {}
    total_tweets, retweet_eq_count, retweet_neq_count, quoted_eq_count, quoted_neq_count = 0, 0, 0, 0, 0
    for tweet in gentweets(src_filepath):
        uid, domains = extract_data(tweet)
        assert str(uid)[-3:] == src_basename
        if len(domains) == 0:
            logging.info('Invalid tweet: {}'.format(tweet))
        else:
            total_tweets += 1

            stripped_data = {'domains': domains}
            if 'quoted_status' in tweet:
                quid, qdomains = extract_data(tweet['quoted_status'])

                if qdomains == stripped_data['domains']:
                    quoted_eq_count += 1
                else:
                    quoted_neq_count += 1

                stripped_data['domains'].update(qdomains)
                stripped_data['quoted'] = quid
            elif 'retweeted_status' in tweet:
                ruid, rdomains = extract_data(tweet['retweeted_status'])

                if rdomains == stripped_data['domains']:
                    retweet_eq_count += 1
                else:
                    retweet_neq_count += 1

                stripped_data['domains'].update(rdomains)
                stripped_data['retweeted'] = ruid

            stripped_data['domains'] = list(stripped_data['domains'])
            if uid not in data:
                data[uid] = []
            data[uid].append(stripped_data)

    with open(dest_filepath, 'w') as dest:
        dest.write(json.dumps(data))

    return total_tweets, retweet_eq_count, retweet_neq_count, quoted_eq_count, quoted_neq_count



if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=(''),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('src_dir', type=str, help='')
    parser.add_argument('dest_dir', type=str, help='')
    args = parser.parse_args()
    
    if not os.path.exists(args.dest_dir):
        os.makedirs(args.dest_dir)

    data = [(f, os.path.join(args.dest_dir, os.path.basename(f))) for f in glob.glob(os.path.join(args.src_dir, '*.json'))]
    pool = Pool(processes=config.NUM_THREADS)
    results = pool.map(mapper, data)
    total_tweets, retweet_eq_count, retweet_neq_count, quoted_eq_count, quoted_neq_count = 0, 0, 0, 0, 0
    for r in results:
        total_tweets += r[0]
        retweet_eq_count += r[1]
        retweet_neq_count += r[2]
        quoted_eq_count += r[3]
        quoted_neq_count += r[4]

    logging.debug('total tweets: {}\nretweet eq: {}, retweet neq: {}\nquoted eq: {}, quoted neq: {}'.format(total_tweets, retweet_eq_count, retweet_neq_count, quoted_eq_count, quoted_neq_count))
