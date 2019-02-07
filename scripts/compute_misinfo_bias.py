import os
import logging
import csv
import argparse
from utils import gen_shares, write_csv, readcol, domain

logging.basicConfig(level=logging.DEBUG)


def compute_misinfo_bias(filepath, misinfo_sites, min_num_shares):
    total_counts = {}
    misinfo_counts = {}
    for uid, tid, domains in gen_shares(filepath):
        if uid not in total_counts:
            total_counts[uid] = 0
        if uid not in misinfo_counts:
            misinfo_counts[uid] = 0

        for d in domains:
            total_counts[uid] += 1
            if d in misinfo_sites:
                misinfo_counts[uid] += 1

    scores = {}
    for uid in misinfo_counts:
        if total_counts[uid] < min_num_shares:
            logging.info('User {} does not have the required minimum number of tweets ({}/{}). Skipping.'.format(
                uid, total_counts[uid], min_num_shares
            ))
            continue
        else:
            scores[uid] = misinfo_counts[uid] / total_counts[uid]
            
    return scores


def mapper(args):
    return compute_misinfo_bias(*args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=('Compute the misinformation scores for a set of users based on'
                     'the domains they share.'),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'domain_shares_file',
        type=str,
        help='The path to a JSON file containing domain shares per user per tweet.'
    )
    parser.add_argument(
        'misinfo_file',
        type=str,
        help='The path to a TAB-separated file containing misinformation domains.'
    )
    parser.add_argument(
        'dest',
        type=str, 
        help='Destination file for the misinformation scores.'
    )
    parser.add_argument(
        '-c',
        '--min_share_count',
        type=int,
        default=10,
        help='The minimum number of tweets a user should have to be included in the analysis.'
    )
    args = parser.parse_args()
    
    if not os.path.exists(args.domain_shares_file) \
       or not os.path.isfile(args.domain_shares_file) \
       or not os.path.exists(args.misinfo_file) \
       or not os.path.isfile(args.misinfo_file):
        print('Invalid domain shares or misinformation input.')
        exit(1)

    if args.min_share_count < 0:
        print('Invalid count: {}'.format(args.min_share_count))
        exit(1)
        
    if not os.path.exists(os.path.dirname(args.dest)):
        os.makedirs(os.path.dirname(args.dest))

    misinfo_sites = frozenset(readcol(args.misinfo_file, skip_rows=1))
    misinfo = compute_misinfo_bias(args.domain_shares_file, misinfo_sites, args.min_share_count)
    write_csv(args.dest, misinfo.items(), ['Twitter ID', 'Misinformation Bias'])
