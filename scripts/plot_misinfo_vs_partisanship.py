import sys
import os
import csv
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
    base_dir = os.path.join(os.getenv('D'), 'measures', 'over-all-tweets')
    d1 = read_dataset(os.path.join(base_dir, 'partisanship.tab'))
    d2 = read_dataset(os.path.join(base_dir, 'misinfo.tab'))
    dest = os.path.join(os.getenv('D'), 'plots', 'misinfo-vs-partisanship.pdf')

    xlabel = 'Political Bias'
    ylabel = 'Misinformation'
    
    x, y = [], []
    for uid in d1:
        if uid in d2:
            x.append(d1[uid])
            y.append(d2[uid])
    xleft, yleft, xright, yright = [], [], [], []
    for i in range(len(x)):
        if x[i] < -.1:
            xleft.append(x[i])
            yleft.append(y[i])
        elif x[i] > .1:
            xright.append(x[i])
            yright.append(y[i])
    print('Dataset length: {}'.format(len(x)))
    print('Pearson correlation: {}'.format(pearsonr(x, y)))

    if len(xleft) > 0:
        print('Pearson correlation (left): {}'.format(pearsonr(xleft, yleft)))

    if len(xright) > 0:
        print('Pearson correlation (right): {}'.format(pearsonr(xright, yright)))
    
    plot(x, y, dest, xlabel, ylabel)
