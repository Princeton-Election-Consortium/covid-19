import numpy as np
import pandas as pd

def compute_fold_change(filename, n_days=3):

    # load data
    data = pd.read_csv(filename, index_col=0)

    # sanity checks
    # TODO: monotonic dates, no repeats, etc

    # fold change over N days
    n_ago = data[:-n_days].values
    fold_change = data[n_days:] / n_ago

    return fold_change

def compute_top_n(filename, n=3, method='last'):

    # load data
    data = pd.read_csv(filename, index_col=0)

    if method == 'last':
        vals = data.iloc[-1]
    elif method == 'sum':
        vals = data.sum(axis=0)

    sort = vals.sort_values()
    is_valid = (~np.isinf(sort)) & (~np.isnan(sort))
    sort = sort[is_valid]
    top = sort.iloc[-n:].index.values

    return top
