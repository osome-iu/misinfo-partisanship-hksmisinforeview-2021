import os
import csv
import glob
import json


def load_stripped_dataset(data_dir):
    users = {}
    for filepath in glob.glob(os.path.join(data_dir, '*.json')):
        with open(filepath, 'r') as f:
            d = json.loads(f.read())
            for raw_uid in d:
                uid = int(raw_uid)
                assert uid not in users
                users[uid] = d[raw_uid]
    return users


def load_bot_scores(filepath):
    scores = {}
    with open(filepath, 'r') as f:
        r = csv.reader(f, delimiter=',')
        next(r)
        for row in r:
            uid = int(row[0])
            score = float(row[3])
            assert uid not in scores
            scores[uid] = score
    return scores


def remove_bot_scores(users_filepath, bot_scores_filepath, dest_filepath):
    users = load_stripped_dataset()
    bot_scores = load_bot_scores()

    new_users = {}
    for uid in users:
        if uid in bot_scores and bot_scores[uid] < 0.8:
            new_users[uid] = users[uid]
            
    logging.debug('Users: {}'.format(len(users)))
    logging.debug('New users: {}'.format(len(new_users)))

    with open(dest_filepath, 'w') as f:
        f.write(json.dumps(new_users))


if __name__ == 'main':
    parser = argparse.ArgumentParser(
        description=(''),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('dataset_dir', type=str, help='')
    parser.add_argument('bot_scores_file', type=str, help='')
    parser.add_argument('dest_file', type=str, help='')
    args = parser.parse_args()
    
    if not os.path.exists(os.path.dirname(args.dest_dir)):
        os.makedirs(os.path.dirname(args.dest_dir))
        
    remove_bot_scores(
        args.dataset_dir,
        args.bot_scores_file,
        args.dest_file
    )
