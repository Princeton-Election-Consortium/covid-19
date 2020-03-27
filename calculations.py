import numpy as np
import pandas as pd

def compute_fold_change(filename, n_days=3):

    # load data
    data = pd.read_csv(filename, index_col=0)

    # sanity checks
    # TODO

    # fold change over N days
    fold_change = data[n_days:] / data[:-n_days].values

    return fold_change
