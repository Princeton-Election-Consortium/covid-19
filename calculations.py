import numpy as np
import pandas as pd

calculation_descriptions = {
        'fold_change': 'Fold change in deaths compared with N days prior',
        'doubling_time': 'Doubling time\nof deaths\n(days)'
        }

def calculate(kind, *args, **kwargs):
    if kind == 'fold_change':
        return compute_fold_change(*args, **kwargs)
    
    elif kind == 'doubling_time':
        return compute_doubling_time(*args, **kwargs)

def compute_fold_change(filename, n_days=3):

    # load data
    data = pd.read_csv(filename, index_col=0)

    # fold change over N days
    fold_change = data.pct_change(n_days) + 1 # +1 for pct change vs fold

    return fold_change

def compute_doubling_time(filename, n_days=3):

    # load data
    data = pd.read_csv(filename, index_col=0)

    # pct change
    change = data.pct_change(n_days)

    # doubling time in units of n_days
    # (if n==1 this is doubling time)
    # (if n==7, it's how many weeks it takes to double)
    dtime = np.log(2) / np.log(1 + change)

    dtime_days = dtime * n_days

    return dtime_days
    
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
