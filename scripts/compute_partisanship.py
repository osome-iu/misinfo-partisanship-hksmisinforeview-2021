import os
import csv
import logging
from multiprocessing import Pool
from utils import readcol, gentweets, write_csv
from urls import domain

logging.basicConfig(level=logging.DEBUG)


def read_polscores(filepath):
    polscores = {}
    with open(filepath, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader) # skip header

        for row in reader:
            if row[0].strip().lower() in polscores:
                logging.debug('Polscore already read for {}'.format(row[0]))
            else:
                polscores[row[0].strip().lower()] = float(row[1])
    return polscores


def compute_partisanship(filepath, polscores, min_num_tweets):
    logging.debug('Processing {}, {}, {}'.format(filepath, len(polscores), min_num_tweets))

    total_counts = {}
    news_visits = {}
    for tweet in gentweets(filepath):
        uid = tweet['user']['id']
        if uid not in total_counts:
            total_counts[uid] = 0
        if uid not in news_visits:
            news_visits[uid] = {}

        if 'entities' in tweet and 'urls' in tweet['entities']:
            for raw_url in tweet['entities']['urls']:
                if raw_url['expanded_url'] is not None:
                    total_counts[uid] += 1
                    url = domain(raw_url['expanded_url'])
                    if url in polscores:
                        if url not in news_visits[uid]:
                            news_visits[uid][url] = 0
                        news_visits[uid][url] += 1

    scores = {}
    for uid in news_visits:
        total_news = sum(news_visits[uid].values())
        total = total_counts[uid]

        if total_news < min_num_tweets:
            logging.info('User {} does not have the required minimum number of tweets ({}/{}). Skipping.'.format(
                uid, total_news, min_num_tweets
            ))
            continue
        else:
            scores[uid] = 0
            for url in news_visits[uid]:
                #scores[uid] += (news_visits[uid][url] / total_news) * polscores[url] # partisanship
                #scores[uid] += (news_visits[uid][url] / total_news) * abs(polscores[url]) # partisanship-abs
                #scores[uid] += (news_visits[uid][url] / total) * polscores[url] # partisanship 2
                scores[uid] += (news_visits[uid][url] / total) * abs(polscores[url]) # partisanship2-abs
    return scores


def mapper(args):
    return compute_partisanship(*args)


if __name__ == '__main__':
    tweets_dir = os.path.join(os.getenv('D'), 'indexed-tweets', 'with-news')
    dest = os.path.join(os.getenv('D'), 'measures', 'over-all-tweets', 'partisanship2-abs', 'with-news.tab')

    #polscores = frozenset(readcol(os.path.join(os.getenv('D'), 'sources', 'news.tab'), skip_rows=1))
    polscores = read_polscores(os.path.join(os.getenv('D'), 'sources', 'news.tab'))
    params = [(os.path.join(tweets_dir, f), polscores, 10) for f in os.listdir(tweets_dir)]
    print(len(polscores))

    pool = Pool(processes=10)
    results = pool.map(mapper, params)

    scores = []
    for r in results:
        scores.extend(r.items())

    if not os.path.exists(os.path.dirname(dest)):
        os.makedirs(os.path.dirname(dest))
    write_csv(dest, scores, ['Twitter ID', 'Partisanship'])
