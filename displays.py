import matplotlib.pyplot as pl
import pandas as pd
import numpy as np
import datetime
import mpld3
    
# Aesthetic parameters
fig_size = (5, 2)

data_line_kw = dict(color = 'darkslateblue',
                    linewidth = 4,
                    )

ref_line_kw = dict(color = 'grey',
                   linewidth = 2,
                    )

def generate_plot(filename):

    # load data
    data = pd.read_csv(filename, index_col=0)

    # select data
    xdata = data.index.values
    ydata = data['Wisconsin'].values

    # plot data
    fig, ax = pl.subplots(figsize=fig_size)
    ax.plot(xdata, ydata, **data_line_kw)

    # axes labels
    xtl = [pd.to_datetime(s).strftime('%-m/%d') for s in xdata]
    ax.set_xticklabels(xtl)

    # convert to html
    html = mpld3.fig_to_html(fig)
    
    #mpld3.show() # TEMPORARY
    #pl.close(fig)

    return html
