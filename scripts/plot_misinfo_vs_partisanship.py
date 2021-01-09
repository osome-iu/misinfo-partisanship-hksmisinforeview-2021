import sys
import os
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import rcParams
from matplotlib.colors import LogNorm

from scipy.stats import pearsonr

AXIS_FONT_SIZE = 12
LABEL_FONT_SIZE = 20

path = ''

def plot(x, y, dest, xlabel, ylabel):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    h, xedges, yedges, _ = plt.hist2d(x, y, bins=40, norm=LogNorm())
    #h = plt.hist2d(x, y, bins=40, norm=LogNorm())
    #plt.colorbar(h[3], ax=ax)

    print(h.shape)
    print(xedges.shape)
    print(yedges.shape)

    print(xedges)
    print(yedges)

    '''
    tmp = os.path.join(os.getenv('D'), 'tmp', 'partisanship-vs-misinformation-hist.csv')
    with open(tmp, 'w') as t:
        w = csv.writer(t, delimiter=',')
        w.writerow(['Partisanship', 'Misinformation', 'Num Users'])
        assert xedges.shape[0] == yedges.shape[0]
        for i in range(xedges.shape[0]-1):
            for j in range(yedges.shape[0]-1):
                w.writerow([float(xedges[i]), float(yedges[j]), float(h[i][j])])
    '''            
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(AXIS_FONT_SIZE)

    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(AXIS_FONT_SIZE)

    #ax.set_xlim(0, 1)
    #ax.set_ylim(0, 1)
    ax.set_xlabel(xlabel, fontsize=LABEL_FONT_SIZE)
    ax.set_ylabel(ylabel, fontsize=LABEL_FONT_SIZE)

    plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
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


def remove_y_outlier(x, y):
    idx = y.index(max(y))
    del x[idx]
    del y[idx]


def remove_x_outlier(x, y):
    idx = x.index(max(x))
    del x[idx]
    del y[idx]


if __name__ == '__main__':
    subf = 'with-retweets'
    
    #base_dir = os.path.join(os.getenv('D'), 'obsolete', 'measures', 'over-all-tweets')
    base_dir = os.path.join(os.getenv('D'), 'measures', subf)
    
    #d1 = read_dataset(os.path.join(base_dir, 'tfidf.tab'))
    #d1 = read_dataset(os.path.join(base_dir, 'partisanship.tab'))
    d1 = read_dataset(os.path.join(base_dir, 'clustering.tab'))

    #d2 = read_dataset(os.path.join(base_dir, 'partisanship-abs.tab'))
    #d2 = read_dataset(os.path.join(base_dir, 'partisanship.tab'))
    d2 = read_dataset(os.path.join(base_dir, 'pollution-filtered.tab'))
    #d2 = read_dataset(os.path.join(base_dir, 'tfidf.tab'))
    #d2 = read_dataset(os.path.join(base_dir, 'clustering.tab'))
    
    dest = os.path.join(os.getenv('D'), 'plots', subf, 'clustering-vs-pollution.pdf')

    xlabel = 'Partisanship'
    ylabel = 'Clustering'

    x, y = [], []
    '''
    tmp = os.path.join(os.getenv('D'), 'tmp', 'partisanship-vs-misinformation-raw.csv')
    with open(tmp, 'w') as t:
        w = csv.writer(t, delimiter=',')
        w.writerow(['User ID', 'Partisanship', 'Misinformation'])
        for uid in d1:
            if uid in d2:
                w.writerow([uid, d1[uid], d2[uid]])
                x.append(d1[uid])
                y.append(d2[uid])
    '''
    for uid in d1:
        if uid in d2:
            x.append(d1[uid])
            y.append(d2[uid])

    # remove outliers
    #remove_y_outlier(x, y)
    #remove_y_outlier(x, y)
    #remove_y_outlier(x, y)
    #remove_x_outlier(x, y)
    #remove_x_outlier(x, y)
    #remove_x_outlier(x, y)
    
    xleft, yleft, xright, yright = [], [], [], []
    for i in range(len(x)):
        if x[i] < 0:
            xleft.append(x[i])
            yleft.append(y[i])
        elif x[i] > 0:
            xright.append(x[i])
            yright.append(y[i])
    print(len(xleft))
    print(len(xright))
    print('Dataset length: {}'.format(len(x)))
    print('Pearson correlation: {}'.format(pearsonr(x, y)))

    if len(xleft) > 0:
        print('Pearson correlation (left): {}'.format(pearsonr(xleft, yleft)))
        print('Average, stdev, x (left): {}, {}'.format(np.average(xleft), np.std(xleft)))
        print('Average, stdev, y (left): {}, {}'.format(np.average(yleft), np.std(yleft)))

    if len(xright) > 0:
        print('Pearson correlation (right): {}'.format(pearsonr(xright, yright)))
        print('Average, stdev, x (right): {}, {}'.format(np.average(xright), np.std(xright)))
        print('Average, stdev, y (right): {}, {}'.format(np.average(yright), np.std(yright)))
    
    plot(x, y, dest, xlabel, ylabel)
