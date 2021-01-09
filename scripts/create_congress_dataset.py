import os
from operator import itemgetter
import Levenshtein
from difflib import SequenceMatcher


def read_file(filepath, name_col, val_col, name_fn, val_fn, skip_first_line, aux_name_col=None, aux_name_fn=None):
    mapping = {}
    with open(filepath, 'rb') as f:
        if skip_first_line:
            f.readline() # skip header
        for line in f:
            parts = [p.strip() for p in line.split(b',')]
            name = name_fn(parts[name_col])
            if aux_name_col is not None:
                assert aux_name_fn is not None
                name = '{}-{}'.format(name, aux_name_fn(parts[aux_name_col]))
            val = val_fn(parts[val_col])
            mapping[name] = val
    return mapping


def read_ideology(filepath):
    return read_file(
        filepath,
        -1, 3,
        lambda x: eval(x.decode('utf-8')).decode('utf-8'),
        float,
        True,
        0,
        lambda x: x.decode('utf-8')
    )


def read_twitter_uids(filepath):
    return read_file(
        filepath,
        0, 1,
        lambda x: x.decode('utf-8'),
        int,
        False
    )


def similarity(s1, s2):
    return sim_difflib(s1, s2)


def sim_difflib(s1, s2):
    return SequenceMatcher(None, s1, s2).ratio()


def sim_levenshtein(s1, s2):
    return Levenshtein.ratio(s1, s2)


def test(s1, s2):
    print('{} <> {}: (difflib, {}), (Levenshtein, {})'.format(
        s1, s2,
        similar_difflib(s1, s2),
        similar_levenshtein(s1, s2)
    ))


def map_ideology(ideology_file, twitter_uids_file):
    ideology = read_ideology(ideology_file)
    twitter_uids = read_twitter_uids(twitter_uids_file)

    print('ideology: {}'.format(len(ideology)))
    print('twitter uids: {}'.format(len(twitter_uids)))

    sims = {}
    for name1 in ideology:
        sims[name1] = {}
        for name2 in twitter_uids:
            sims[name1][name2] = similarity(name1, name2)

    for name in sims:
        sorted_items = sorted(sims[name].items(), key=itemgetter(1), reverse=True)
        name_alt = sorted_items[0][0]
        sim = sorted_items[0][1]
        print('{},{},{},{},{}'.format(
            twitter_uids[name_alt],
            ideology[name],
            name, name_alt, sim
        ))


if __name__ == '__main__':
    data_dir = os.path.join(os.getenv('D'), 'congress')
    suffix = 'house'
    map_ideology(
        os.path.join(data_dir, 'ideology-{}.csv'.format(suffix)),
        os.path.join(data_dir, 'twitter-uids-{}.csv'.format(suffix))
    )
    
