import os
import argparse
import csv
import logging
from operator import itemgetter


def main():
    parser = argparse.ArgumentParser(
        description=("Reduce key-value pairs by applying the reduce function "
                     "to values with the same key."),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('reduce_fn', type=str, 
                        help='A function in python that can be applied to an iterable.')
    parser.add_argument('source_files', type=str, nargs='+',
                        help=('A list of tab-separated files or directories containing '
                              'tab-separated files with the keys in column 0, '
                              'and the values in column 1 that are to be reduced.'))
    parser.add_argument('dest', type=str, 
                        help='The file where the reduced data will be written.')
    parser.add_argument('--key_convert_fn', type=str,
                        help='A function to be applied to each key, e.g. to convert it to the correct data type.')
    parser.add_argument('--value_convert_fn', type=str,
                        help='A function to be applied to each value, e.g. to convert it to the correct data type.')
    parser.add_argument('--sort', type=str, choices=['yes', 'reverse'],
                        help="Should the final output be sorted and how?")
    parser.add_argument('--skip_rows', type=int, default=0,
                        help='The number of header rows in the source files to skip.')
    parser.add_argument('-hdrs', '--headers', type=str, nargs='+',
                        help=('The column headers in the destination file. '))
    
    args = parser.parse_args()

    try:
        reduce = eval(args.reduce_fn)
    except:
        logging.info('Invalid reduce function: %s', args.reduce_fn)
        exit(1)

    key_convert_fn = lambda x: x
    if args.key_convert_fn is not None:
        try:
            key_convert_fn = eval(args.key_convert_fn)
        except:
            logging.info('Invalid key_convert_fn: %s', args.key_convert_fn)
            exit(1)

    value_convert_fn = lambda x: x
    if args.value_convert_fn is not None:
        try:
            value_convert_fn = eval(args.value_convert_fn)
        except:
            logging.info('Invalid value_convert_fn: %s', args.value_convert_fn)
            exit(1)

    if args.sort is not None:
        if args.sort.lower() != 'yes' and args.sort.lower() != 'reverse':
            logging.info("Invalid sort argument. Should be 'yes' or 'reverse'.")
            exit(1)

    source_files = []
    for filepath in args.source_files:
        if not os.path.exists(filepath):
            raise ValueError('File does not exist: %s' % filepath)
        elif os.path.isdir(filepath):
            source_files.extend([os.path.join(filepath, f) for f in os.listdir(filepath)])
        else:
            source_files.append(filepath)

    d = {}
    for filepath in source_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            r = csv.reader(f, delimiter='\t')
            if args.skip_rows is not None:
                for _ in range(args.skip_rows):
                    next(r)
            for row in r:
                assert len(row) >= 2
                k = key_convert_fn(row[0])
                v = value_convert_fn(row[1])
                if k in d:
                    d[k] = reduce([d[k], v])
                else:
                    d[k] = v

    if args.sort is None:
        rows = d.items()
    elif args.sort == 'yes':
        rows = sorted(d.items(), key=itemgetter(1))
    elif args.sort == 'reverse':
        rows = sorted(d.items(), key=itemgetter(1), reverse=True)
    else:
        logging.info('Invalud sort option.')
        exit(1)

    if args.headers is not None:
        rows.insert(0, args.headers)

    if not os.path.exists(os.path.dirname(args.dest)):
        os.makedirs(os.path.dirname(args.dest))
        
    with open(args.dest, 'w', encoding='utf-8') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerows(rows)


if __name__ == '__main__':
    main()
