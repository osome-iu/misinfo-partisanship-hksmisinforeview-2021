import sys
import os
import logging
import argparse
import csv
from multiprocessing import Pool
from config import DEBUG_LEVEL
from utils import readcol
from urls import domain

sys.path.append(os.path.join(os.getenv('C'), 'scripts', 'workers'))
from strip_tweets_worker import strip_tweets

logging.basicConfig(level=DEBUG_LEVEL)


def read_misinfo_domains(misinfo_sources_filepath, misinfo_cat):
    domains = set()
    with open(misinfo_sources_filepath, 'r') as f:
        r = csv.reader(f, delimiter='\t')
        next(r) # skip header
        for row in r:
            d = domain(row[0])
            cats = set([cat.lower() for cat in row[1:4]])
            if misinfo_cat in cats and not d in domains:
                domains.add(d)
    return domains

            
def mapper(args):
    return strip_tweets(*args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=('Create a separate dataset of tweets only pertaining '
                     'to one of the categories of misinformation in the '
                     'OpenSources dataset, such as clickbait, conspiracy, '
                     'fake, junksci, unreliable, rumor, satire, hate, '
                     'political, bias. Only tweets containing one or more '
                     'links to one  of the domains matching the misinfo '
                     'category will be kept in the resulting dataset.'),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('num_threads', type=int, default=1, 
                        help='Number of threads to distribute the source files amongst.')
    parser.add_argument('raw_tweets_dir', type=str, 
                        help='A directory containing files with the raw tweets.')
    parser.add_argument('misinfo_sources', type=str,
                        help=('A TAB separated file with domains in the first column, '
                              'and category labels on subsequent columns.'))
    parser.add_argument('misinfo_cat', type=str,
                        help='The misinformation category to which domains must belong.')
    parser.add_argument('dest_dir', type=str, 
                        help='A directory where the new tweets will be placed.')
    args = parser.parse_args()
    
    if not os.path.exists(args.dest_dir):
        os.makedirs(args.dest_dir)

    misinfo_domains = read_misinfo_domains(args.misinfo_sources, args.misinfo_cat)

    data = [
        (os.path.join(args.raw_tweets_dir, f),
         os.path.join(args.dest_dir,
                      os.path.basename(f)[:-3] if os.path.basename(f)[-3:] == '.gz'
                      else os.path.basename(f)),
         misinfo_domains,
         None
        )
        for f in os.listdir(args.raw_tweets_dir)
    ]
    pool = Pool(processes=args.num_threads)
    pool.map(mapper, data)
