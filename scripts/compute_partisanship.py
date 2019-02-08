'''
compute_partisanship.py

Computes the political bias for a set of users based on the domains
from which they share. The script relies on an external list of
misinformation domains, which can be obtained from OpenSources.co.

'''
import os
import logging
import csv
import argparse
from utils import gen_shares, domain, write_csv

logging.basicConfig(level=logging.DEBUG)


def read_valences(filepath):
    valences = {}
    with open(filepath, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader) # skip header

        for row in reader:
            if row[0].strip().lower() in valences:
                logging.debug('Polscore already read for {}'.format(row[0]))
            else:
                valences[row[0].strip().lower()] = float(row[1])
    return valences


def compute_partisanship(filepath, valences, min_num_shares):
    total_counts = {}
    news_visits = {}
    for uid, tid, domains in gen_shares(filepath):
        if uid not in total_counts:
            total_counts[uid] = 0
        if uid not in news_visits:
            news_visits[uid] = {}

        for d in domains:
            total_counts[uid] += 1
            if d in valences:
                if d not in news_visits[uid]:
                    news_visits[uid][d] = 0
                news_visits[uid][d] += 1

    scores = {}
    for uid in news_visits:
        total_news = sum(news_visits[uid].values())
        total = total_counts[uid]

        if total < min_num_shares:
            logging.info('User {} does not have the required minimum number of tweets ({}/{}). Skipping.'.format(
                uid, total_news, min_num_shares
            ))
            continue
        else:
            scores[uid] = 0
            for d in news_visits[uid]:
                scores[uid] += (news_visits[uid][d] / total) * valences[d]
                
    return scores


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=('Compute the partisanship scores for a set of users based on'
                     'the domains they share.'),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'domain_shares_file',
        type=str,
        help='The path to a JSON file containing domain shares per user per tweet.'
    )
    parser.add_argument(
        'political_valence_file',
        type=str,
        help=('The path to a TAB-separated file containing political valences for'
              'selected domains.')
    )
    parser.add_argument(
        'dest',
        type=str, 
        help='Destination file for the partisanship scores.'
    )
    parser.add_argument(
        '-c',
        '--min_share_count',
        type=int,
        default=10,
        help='The minimum number of domains a user shared to be included in the analysis.'
    )
    args = parser.parse_args()
    
    if not os.path.exists(args.domain_shares_file) \
       or not os.path.isfile(args.domain_shares_file) \
       or not os.path.exists(args.political_valence_file) \
       or not os.path.isfile(args.political_valence_file):
        print('Invalid domain shares or political valences input.')
        exit(1)

    if args.min_share_count < 0:
        print('Invalid count: {}'.format(args.min_share_count))
        exit(1)
        
    if not os.path.exists(os.path.dirname(args.dest)):
        os.makedirs(os.path.dirname(args.dest))

    valences = read_valences(args.political_valence_file)
    partisanships = compute_partisanship(args.domain_shares_file, valences, args.min_share_count)
    write_csv(args.dest, partisanships.items(), ['Twitter ID', 'Partisanship'])
