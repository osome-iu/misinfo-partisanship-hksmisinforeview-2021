'''
plot_partisanship_vs_misinfo.py

Creates a density plot given a set of users with two types of
scores. Use this script to plot the misinformation and political bias
scores computed in other parts of the workflow.
'''

import sys
import os
import csv
import argparse
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import rcParams
from matplotlib.colors import LogNorm

from scipy.stats import pearsonr

AXIS_FONT_SIZE = 12
LABEL_FONT_SIZE = 20


def plot(x, y, dest, xlabel, ylabel):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    h = plt.hist2d(x, y, bins=40, norm=LogNorm())
    plt.colorbar(h[3], ax=ax)

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(AXIS_FONT_SIZE)

    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(AXIS_FONT_SIZE)

    ax.set_xlabel(xlabel, fontsize=LABEL_FONT_SIZE)
    ax.set_ylabel(ylabel, fontsize=LABEL_FONT_SIZE)

    plt.tight_layout()

    pp = PdfPages(dest)
    fig.savefig(pp, format='pdf')
    pp.close()
    plt.close()


def read_dataset(filepath):
    dataset = {}
    with open(filepath, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)
        for row in reader:
            uid = int(row[0])
            measure = float(row[1])
            if measure != 0:
                dataset[uid] = measure
    return dataset


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=('Compute the partisanship scores for a set of users based on'
                     'the domains they share.'),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'partisanship',
        type=str,
        help='The path to a TAB-separated file with partisanship scores.'
    )
    parser.add_argument(
        'misinfo',
        type=str,
        help='The path to a TAB-separated file with misinfo scores.'
    )
    parser.add_argument(
        'dest',
        type=str, 
        help='Destination PDF for the plot.'
    )
    args = parser.parse_args()
    
    if not os.path.exists(args.partisanship) \
       or not os.path.isfile(args.partisanship) \
       or not os.path.exists(args.misinfo) \
       or not os.path.isfile(args.misinfo):
        print('Invalid partisanship or misinfo input.')
        exit(1)
        
    if not os.path.exists(os.path.dirname(args.dest)):
        os.makedirs(os.path.dirname(args.dest))

    p = read_dataset(args.partisanship)
    m = read_dataset(args.misinfo)

    xlabel = 'Political Bias'
    ylabel = 'Misinformation'
    
    x, y = [], []
    for uid in p:
        if uid in m:
            x.append(p[uid])
            y.append(m[uid])
    print('Dataset length: {}'.format(len(x)))

    xleft, yleft, xright, yright = [], [], [], []
    for i in range(len(x)):
        if x[i] < -.1:
            xleft.append(x[i])
            yleft.append(y[i])
        elif x[i] > .1:
            xright.append(x[i])
            yright.append(y[i])
            
    if len(xleft) > 0:
        print('Pearson correlation (left): {}'.format(pearsonr(xleft, yleft)))

    if len(xright) > 0:
        print('Pearson correlation (right): {}'.format(pearsonr(xright, yright)))
    
    plot(x, y, args.dest, xlabel, ylabel)
