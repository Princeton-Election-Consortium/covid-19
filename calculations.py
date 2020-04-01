import numpy as np
import pandas as pd

calculation_descriptions = {
        'fold_change': 'Fold change in\n{var} compared\nwith 3 days prior',
        'doubling_time': 'Time for {var}\nto double\n(days)'
        }

var_replacements = {
        'confirmed': 'cases'
        }

def c_str(kind, var):
    var = var_replacements.get(var.lower(), var.lower())
    return calculation_descriptions[kind].format(var=var)

def calculate(kind, *args, **kwargs):
    """Wrapper for all relevant calculations in this module.
    """

    if kind == 'fold_change':
        return compute_fold_change(*args, **kwargs)
    
    elif kind == 'doubling_time':
        return compute_doubling_time(*args, **kwargs)

def compute_fold_change(filename, n_days=3):
    """For each column, compute daily fold change relative to n days prior

    filename: path to scraped data table
    """

    # load data
    data = pd.read_csv(filename, index_col=0)

    # fold change over N days
    fold_change = data.pct_change(n_days) + 1 # +1 for pct change to fold

    if reverse:
        fold_change.iloc[::-1]

    return fold_change

def compute_doubling_time(filename, n_days=3):
    """For each column, compute daily doubling time estimate, defined as ln(2)/ln(growth rate). Growth rate estimate for any given day is made using change relative to n_days ago.

    filename: path to scraped data table
    """

    # load data
    data = pd.read_csv(filename, index_col=0)

    # pct change
    change = data.pct_change(n_days)

    # doubling time in units of n_days
    # (if n==1 this is doubling time in days, i.e. how many days it takes to double)
    # (if n==7, it's in weeks, i.e. how many weeks it takes to double)
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
