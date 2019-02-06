import os
import argparse
import csv
import logging
from operator import itemgetter
from urls import domain
from config import DEBUG_LEVEL

logging.basicConfig(level=DEBUG_LEVEL)

'''
This list of exceptions was obtained later in the analysis process
once we could see what the most popular domains were. Except
whitehouse.gov, all these domains are excluded because they are not
overtly political, but they generate a lot of traffic, and so without
them, the size of the tweet dataset is smaller and more
manageable. whitehouse.gov was removed because its political valence
seems likely to change depending on whether there is a Democrat or a
Republican in the White House. This assumptions is not empirically
verified, but it is better to be safe and exclude it.
'''
EXCEPTIONS = frozenset([

])

def read_domain_data(filepath, domain_col, data_cols_to_read, delimiter, skip_rows):
    domains = {}
    row_count = 0 # for debugging

    with open(filepath, 'r') as f:
        reader = csv.reader(f, delimiter=delimiter)

        # skip headers
        if skip_rows is not None:
            for _ in range(skip_rows):
                row_count += 1
                next(reader)
        
        # process the rows
        for row in reader:
            if domain_col >= len(row):
                raise ValueError('Invalid domain index: {}, {}'.format(domain_col, ', '.join(row)))
            d = domain(row[domain_col])

            if d in domains:
                logging.info('Domain has already been processed: {}. Skipping new values.'.format(d))
                logging.info('Existing data: {}'.format(', '.join(domains[d])))
                logging.info('New data: {}'.format(', '.join(row)))

            new_row = []
            if data_cols_to_read is not None:
                for idx in data_cols_to_read:
                    if idx >= len(row):
                        raise ValueError('Invalid index: {}, {}'.format(idx, ', '.join(row)))
                    elif idx == domain_col:
                        logging.info('Data column the same as the domain column. Skipping.')
                    else:
                        new_row.append(row[idx])

            row_count += 1
            domains[d] = new_row
    return domains


def main():
    parser = argparse.ArgumentParser(
        description=('Create a list of domains with standardized URLs.'
                     'Do this either from a primary CSV or from a provided list.'),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('dest_file', type=str, 
                        help=('Destination file for the combined data. '
                              'The normalized domain will always be in the first column, '
                              'followed by the columns to keep from the primary file, '
                              'followed by the columns to keep from the secondary file.'))

    parser.add_argument('-p', '--primary_csv', type=str, 
                        help=('A CSV file containing domains. '
                              'All domains from this file will be kept in the final output.'))

    parser.add_argument('-s', '--secondary_csv', type=str, default=None,
                        help=('A CSV containing domain data. '
                              'Domains from this file will not be kept '
                              'unless they appear in the primary file.'))

    parser.add_argument('-domain1', '--primary_domain_col', type=int, default=0,
                        help='The column with the domain in the primary source file.')

    parser.add_argument('-data1', '--primary_data_cols', type=int, nargs='+',
                        help='Columns with additional data from the primary source file to keep in the output.')

    parser.add_argument('-delim1', '--primary_delim', type=str, default='\t',
                        help='The delimiter in the primary source file.')

    parser.add_argument('-skip1', '--primary_skip_rows', type=int, default=0,
                        help='The number of header rows in the primary source file to skip.')

    parser.add_argument('-domain2', '--secondary_domain_col', type=int, default=0,
                        help='The column with the domain in the secondary source file.')

    parser.add_argument('-data2', '--secondary_data_cols', type=int, nargs='+',
                        help='Columns with additional data from the secondary source file to keep in the output..')

    parser.add_argument('-delim2', '--secondary_delim', type=str, default='\t',
                        help='The delimiter in the secondary source file.')

    parser.add_argument('-skip2', '--secondary_skip_rows', type=int, default=0,
                        help='The number of header rows in the secondary source file to skip.')

    parser.add_argument('-ddelim', '--dest_delim', type=str, default='\t',
                        help='The delimiter in the destination file.')

    parser.add_argument('-dhead', '--dest_col_headers', type=str, nargs='+',
                        help=('The column headers in the destination file. '
                              'Must match the number of columns being kept from both source files, '
                              'plus the first column for the domain.'))

    parser.add_argument('-exclude', '--exclude_domains', type=str, nargs='+',
                        help='A list of domains to exclude.')

    parser.add_argument('-include', '--include_domains', type=str, nargs='+',
                        help='A list of additional domains to include in the final list.')

    args = parser.parse_args()

    if os.path.dirname(args.dest_file) != '' and not os.path.exists(os.path.dirname(args.dest_file)):
        os.makedirs(os.path.dirname(args.dest_file))

    if (args.primary_csv is None or not os.path.exists(args.primary_csv)) and args.include_domains is None:
        raise ValueError('No input provided.')

    # read the CSVs
    logging.debug('Reading primary file.')
    if args.primary_csv is not None:
        primary_data = read_domain_data(
            args.primary_csv,
            args.primary_domain_col,
            args.primary_data_cols,
            args.primary_delim,
            args.primary_skip_rows
        )
    else:
        primary_data = {}

    if args.include_domains is not None:
        for raw_d in args.include_domains:
            d = domain(raw_d)
            if d not in primary_data:
                primary_data[d] = []

    logging.debug('Reading secondary file.')
    if args.secondary_csv is not None:
        secondary_data = read_domain_data(
            args.secondary_csv,
            args.secondary_domain_col,
            args.secondary_data_cols,
            args.secondary_delim,
            args.secondary_skip_rows
        )
    else:
        secondary_data = {}

    # combine the data from both files into rows
    excluded_domains = frozenset(args.exclude_domains) if args.exclude_domains is not None else frozenset()
    combined_rows = []
    for d in primary_data.keys():
        if d in excluded_domains:
            logging.info('Skipping {}'.format(d))
            continue
        new_row = [d]
        new_row.extend(primary_data[d])
        if d in secondary_data:
            new_row.extend(secondary_data[d])
        combined_rows.append(new_row)
    sorted_data = sorted(combined_rows)

    # write the data to the dest file
    logging.debug('Writing combined file.')
    with open(args.dest_file, 'w') as f:
        writer = csv.writer(f, delimiter=args.dest_delim)
        if args.dest_col_headers is not None:
            sorted_data.insert(0, args.dest_col_headers)
        else:
            sorted_data.insert(0, ['domain'])

        writer.writerows(sorted_data)


if __name__ == '__main__':
    main()
