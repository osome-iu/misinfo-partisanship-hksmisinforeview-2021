import os
import csv
import matplotlib
matplotlib.use('Agg')
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn import datasets


def load_data(filepath):
    with open(filepath, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        header = next(reader)

        data_labels = np.array(header[1:])
        print(data_labels)
        target_header = header[0]
        print(target_header)

        data = []
        targets = []
        for row in reader:
            data.append(list(map(float, row[1:])))
            targets.append(float(row[0]))

    ddf = pd.DataFrame(data, columns=data_labels)
    tdf = pd.DataFrame(targets, columns=[target_header])

    return ddf, tdf


def regression(data, target, x_labels, y_label):
    X = data[x_labels]
    X = sm.add_constant(X)
    y = target[y_label]

    # Note the difference in argument order
    model = sm.OLS(y, X).fit()
    predictions = model.predict(X) # make the predictions by the model

    # Print out the statistics
    print(model.summary())


if __name__ == '__main__':
    retweets = True

    subf = 'with-retweets' if retweets else 'without-retweets'
    left_data, left_target = load_data(os.path.join(os.getenv('D'), 'measures', subf, 'regression-left.tab'))
    right_data, right_target = load_data(os.path.join(os.getenv('D'), 'measures', subf, 'regression-right.tab'))
    all_data, all_target = load_data(os.path.join(os.getenv('D'), 'measures', subf, 'regression-all.tab'))

    data, target = left_data, left_target
    #data, target = right_data, right_target
    #data, target = all_data, all_target


    regression(
        data, target,
        x_labels=['Partisanship', 'Clustering', 'TF-IDF'],
        y_label='Pollution'
    )

    '''
    regression(
        data, target,
        x_labels=['Clustering', 'TF-IDF'],
        y_label='Pollution'
    )
    '''
    '''
    regression(
        data, target,
        x_labels=['Partisanship', 'Clustering'],
        y_label='Pollution'
    )
    '''
    '''
    regression(
        data, target,
        x_labels=['Partisanship', 'TF-IDF'],
        y_label='Pollution'
    )
    '''

    

    
