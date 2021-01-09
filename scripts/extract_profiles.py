import os
import json
import pprint
import csv
import re
from operator import itemgetter
from nltk.corpus import stopwords


def read_tweets(data_dir):
    tweets = []
    for dataf in os.listdir(data_dir):
        with open(os.path.join(data_dir, dataf), 'r') as f:
            for line in f:
                tweets.append(json.loads(line.strip()))
    return tweets


def load_measure(filepath):
    measures = {}
    with open(filepath, 'r') as f:
        r = csv.reader(f, delimiter='\t')
        next(r) # skip header
        for row in r:
            uid = int(row[0])
            v = float(row[1])
            measures[uid] = v
    return measures


def extract_profile_descs(tweets):
    delims_pattern = re.compile('[# ]')
    descs = {}
    for t in tweets:
        uid = int(t['user']['id_str'])
        assert uid not in descs

        if 'description' not in t['user']:
            descs[uid] = None
        else:
            descs[uid] = {}

            tokens_raw = [tkn.strip() for tkn in t['user']['description'].split()]
            tokens = []
            for tkn in tokens_raw:
                if '#' not in tkn:
                    tokens.append(tkn)
                else:
                    hashtags = tkn.split('#')
                    for ht in hashtags:
                        if len(ht) > 0:
                            tokens.append('#{}'.format(ht))
                
            for tkn in tokens:
                if len(tkn) == 0:
                    continue
                
                if tkn not in descs[uid]:
                    descs[uid][tkn] = 1
                else:
                    descs[uid][tkn] += 1
        
    return descs


def compute_token_freqs(descs, uids):
    tokens = {}
    for uid in descs:
        if uid in uids:
            for tkn in descs[uid]:
                if tkn not in tokens:
                    tokens[tkn] = descs[uid][tkn]
                else:
                    tokens[tkn] += descs[uid][tkn]
    return tokens


def remove_stopwords(freqs):
    new_freqs = {}
    en_stops = set(stopwords.words('english'))
    for word_raw in freqs:
        if not word_raw[-1].isalnum():
            word = word_raw[:-1]
        else:
            word = word_raw
            
        if len(word) > 1 and word.lower() not in en_stops:
            new_freqs[word] = freqs[word_raw]
    return new_freqs


def write_freqs(freqs, filepath, hashtags_only=False):
    with open(filepath, 'w') as f:
        w = csv.writer(f, delimiter='\t')
        for word, freq in sorted(freqs.items(), key=itemgetter(1), reverse=True):
            if (not hashtags_only) or (hashtags_only and word[0] == '#'):
                w.writerow([word, freq])


def write_freqs_to_text(freqs, filepath, hashtags_only=False):
    with open(filepath, 'w') as f:
        for word, freq in sorted(freqs.items(), key=itemgetter(1), reverse=True):
            if (not hashtags_only) or (hashtags_only and word[0] == '#'):
                f.write(' '.join([word] * freq))
                f.write('\n')

    
if __name__ == '__main__':
    partisanship = load_measure(os.path.join(os.getenv('D'), 'measures', 'with-retweets', 'partisanship.tab'))
    tweets = read_tweets(os.path.join(os.getenv('D'), 'single-tweets'))
    descs = extract_profile_descs(tweets)

    left = set(filter(lambda uid: partisanship[uid] < 0 and descs[uid], descs.keys()))
    right = set(filter(lambda uid: partisanship[uid] > 0 and descs[uid], descs.keys()))
    center = set(filter(lambda uid: partisanship[uid] == 0 and descs[uid], descs.keys()))

    print(len(left))
    print(len(right))
    
    left_t = remove_stopwords(compute_token_freqs(descs, left))
    right_t = remove_stopwords(compute_token_freqs(descs, right))
    
    sorted_left = sorted(left_t.items(), key=itemgetter(1), reverse=True)
    sorted_right = sorted(right_t.items(), key=itemgetter(1), reverse=True)

    dest_dir = os.path.join(os.getenv('D'), 'profile-descs')

    write_freqs(left_t, os.path.join(dest_dir, 'left-all.tsv'))
    write_freqs(left_t, os.path.join(dest_dir, 'left-hashtags.tsv'), hashtags_only=True)
    write_freqs_to_text(left_t, os.path.join(dest_dir, 'left-all.txt'))
    write_freqs_to_text(left_t, os.path.join(dest_dir, 'left-hashtags.txt'), hashtags_only=True)


    write_freqs(right_t, os.path.join(dest_dir, 'right-all.tsv'))
    write_freqs(right_t, os.path.join(dest_dir, 'right-hashtags.tsv'), hashtags_only=True)
    write_freqs_to_text(right_t, os.path.join(dest_dir, 'right-all.txt'))
    write_freqs_to_text(right_t, os.path.join(dest_dir, 'right-hashtags.txt'), hashtags_only=True)
