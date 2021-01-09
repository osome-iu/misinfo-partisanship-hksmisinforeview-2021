import os
import random
import glob
import argparse
import logging
import numpy
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib import rc
from matplotlib.backends.backend_pdf import PdfPages

from utils import readcol

rc('text', usetex=True)

logging.basicConfig(level=logging.DEBUG)


def plot_misinfo(files, title, dest):
    data = []
    labels = []
    for f in files:
        if not f.endswith('with-factchecking.tab') and not f.endswith('with-news.tab') and not f.endswith('with-misinfo.tab'):
            print(f)
            curr_data = readcol(f, col=1, skip_rows=1, apply_fn=float)
            if len(curr_data) > 0:            
                label = os.path.splitext(os.path.basename(f))[0]
                label = label[label.index('-')+1:]
                data.append((numpy.median(curr_data), curr_data, label))
    sorted_data = sorted(data)
    data = [d[1] for d in sorted_data]
    labels = [d[2].replace('misinfo-', '') for d in sorted_data]

    fig, ax = plt.subplots()
    ax.set_title(title, fontsize=24)
    ax.boxplot(data, notch=True, showfliers=False, showmeans=True)
    plt.xticks(range(1, len(labels) + 1), labels, rotation=20)
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(12)
    ax.set_ylabel('$B_{h}$', fontsize=20, rotation='horizontal', labelpad=17)
    pp = PdfPages(dest)
    fig.savefig(pp, format='pdf')
    pp.close()

    
def plot_main(files, title, dest):
    data = []
    labels = []
    for f in files:
        if f.endswith('with-factchecking.tab') or f.endswith('with-news.tab') or f.endswith('with-misinfo.tab'):
            print(f)
            curr_data = readcol(f, col=1, skip_rows=1, apply_fn=float)
            if len(curr_data) > 0:            
                label = os.path.splitext(os.path.basename(f))[0]
                label = label[label.index('-')+1:]
                data.append((numpy.median(curr_data), curr_data, label))
    sorted_data = sorted(data)
    data = [d[1] for d in sorted_data]
    labels = [d[2] for d in sorted_data]
    for i in range(len(labels)):
        if labels[i] == 'misinfo':
            labels[i] = 'online pollution'
        elif labels[i] == 'factchecking':
            labels[i] = 'fact checking'

    fig, ax = plt.subplots()
    ax.set_title(title, fontsize=24)
    ax.boxplot(data, notch=True, showfliers=False, showmeans=True)
    plt.xticks(range(1, len(labels) + 1), labels)
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(18)
    ax.set_ylabel('$B_{h}$', fontsize=20, rotation='horizontal', labelpad=17)
    pp = PdfPages(dest)
    fig.savefig(pp, format='pdf')
    pp.close()


def plot(files, title, dest):
    return plot_main(files, title, dest)


def argparse_plot():
    parser = argparse.ArgumentParser(
        description=('Box plot of the given measure for different datasets.'),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('measure_dir', type=str, 
                        help='A directory containing files with the measure computations.')
    parser.add_argument('--title', type=str,
                        help='The title for the plot.')
    parser.add_argument('--pattern', type=str,
                        help='Filename pattern for the input files.')
    parser.add_argument('dest_file', type=str, 
                        help='PDF file where to store the plot.')
    args = parser.parse_args()
    
    if not os.path.exists(os.path.dirname(args.dest_file)):
        os.makedirs(os.path.dirname(args.dest_file))

    if args.pattern is None:
        files = glob.glob(os.path.join(args.measure_dir, '*'))
    else:
        files = glob.glob(os.path.join(args.measure_dir, args.pattern))
        
    plot(files, '' if args.title is None else args.title, args.dest_file)


def hardcode_plot():
    '''
    plot(
        sorted(glob.glob(os.path.join(os.getenv('D'), 'measures', 'over-all-tweets', 'hbias', 'with-*'))),
        'HBias (full dataset, over all tweets)',
        os.path.join(os.getenv('D'), 'plots', 'all-tweets-with.pdf')
    )
    plot(
        sorted(glob.glob(os.path.join(os.getenv('D'), 'measures', 'over-tweets-sample', 'hbias', 'with-*'))),
        'HBias (full dataset, over tweets sample)',
        os.path.join(os.getenv('D'), 'plots', 'sample-tweets-with.pdf')
    )
    plot(
        sorted(glob.glob(os.path.join(os.getenv('D'), 'measures', 'over-tweets-partition', 'hbias', 'with-*'))),
        'HBias (full dataset, over tweets partition)',
        os.path.join(os.getenv('D'), 'plots', 'partition-tweets-with.pdf')
    )

    plot(
        sorted(glob.glob(os.path.join(os.getenv('D'), 'measures', 'over-all-tweets', 'hbias', 'only-*'))),
        'HBias (reduced dataset, over all tweets)',
        os.path.join(os.getenv('D'), 'plots', 'all-tweets-only.pdf')
    )
    plot(
        sorted(glob.glob(os.path.join(os.getenv('D'), 'measures', 'over-tweets-sample', 'hbias', 'only-*'))),
        'HBias (reduced dataset, over tweets sample)',
        os.path.join(os.getenv('D'), 'plots', 'sample-tweets-only.pdf')
    )
    plot(
        sorted(glob.glob(os.path.join(os.getenv('D'), 'measures', 'over-tweets-partition', 'hbias', 'only-*'))),
        'HBias (reduced dataset, over tweets partition)',
        os.path.join(os.getenv('D'), 'plots', 'partition-tweets-only.pdf')
    )
    '''
    plot(
        sorted(glob.glob(os.path.join(os.getenv('D'), 'measures', 'over-tweets-partition', 'hbias', 'with-*'))),
        '$B_{h}$ for three main types of users',
        os.path.join(os.getenv('D'), 'plots', 'partition-tweets-with.pdf')
    )


if __name__ == '__main__':
    hardcode_plot()
