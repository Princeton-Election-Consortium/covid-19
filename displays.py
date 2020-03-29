import os
import matplotlib.pyplot as pl
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.transforms import blended_transform_factory as blend
import seaborn as sns
from imageio import imwrite
from PIL import Image
import pandas as pd
import numpy as np
import datetime
    
# Aesthetic parameters
fig_size = (9, 5.5)
size_scale = fig_size[0] / 18
ax_box = [0.25, 0.15, 0.62, 0.8]

# font sizes
tfs = 25 * size_scale # title font size
lfs = 25 * size_scale# series label font size
ylfs = 30 * size_scale # ylabel font size
xtkfs = 25 * size_scale # xtick font size
ytkfs = 30 * size_scale # ytick font size

# ticks
tpad = 7 * size_scale
tlen = 10 * size_scale
n_yticks = 8

# label positions
title_pos = (0.05, 0.94)
ylab_pos = (-0.24, 0.5)
min_dist_factor = 0.06

# axes limits
ylims = (0.0, None)

# line formatting
sns_cols = [(0, 0, 0)] + sns.color_palette('deep')
data_linewidth = 4 * size_scale
data_line_color = 'darkslateblue'

def choose_y(pos, priors, min_dist=0.3, inc=0.01):
    """Adjust a y coordinate such that it stays a min distance from list of other coordinates
    """
    priors = np.array(priors)

    if len(priors) == 0:
        return pos
    
    dif = pos - priors
    closest = np.min(np.abs(dif))
    closest_i = np.argmin(np.abs(dif))
    while closest < min_dist:
        inc_ = inc * np.sign(dif[closest_i])
        pos += inc_
        closest = np.min(np.abs(pos - priors))

    return pos

def generate_plot(filename, columns, title='', ylabel='', log=False, bolds=[], min_date=None, name='plot', out_dir='images', fmt='png'):
    """Returns numpy array with image of full figure

    filename : relative path to csv with values to plot
    columns : str of list thereof of column names to plots
    title : optional string at title on plot
    ylabel : optional string as ylabel on plot
    log : use log scale on y axis
    bolds : list of indices parallel to `columns` whose label to bold
    min_date : minimum date to plot
    """

    # process params
    if not isinstance(columns, (list, np.ndarray)):
        columns = [columns]
    if not title and len(columns) == 1:
        title = columns[0]

    # load data
    data = pd.read_csv(filename, index_col=0)

    # process data for display purposes
    for col in columns:
        sdat = data[col].values
        isnan = np.isnan(sdat)
        first_nonnan = np.argwhere(isnan == False)[0][0]
        sdat[:first_nonnan + 3] = np.nan
        data[col] = sdat
    if min_date is not None:
        data = data[pd.to_datetime(data.index) >= min_date]

    # setup axes
    fig = pl.figure(figsize=fig_size)
    canvas = FigureCanvas(fig)
    ax = fig.add_axes(ax_box) 

    # plot data
    colors = sns_cols[:len(columns)]
    for col_idx, (column, color) in enumerate(zip(columns, colors)):
        # specify data
        ydata = data[column].values
        ydata[np.isinf(ydata)] = np.nan
        xdata = np.arange(len(ydata))

        # aesthetic prep
        if len(columns) > 1:
            data_line_color = color
        lw = data_linewidth
        if col_idx in bolds:
            lw *= 2

        # plot line
        ax.plot(xdata, ydata, lw=lw, color=data_line_color)

    # plot reference data
    ref = 3
    ax.axhspan(0, ref, color='lightcoral', alpha=0.3, lw=0)
    ax.text(.17, .04, 'RUNAWAY SPREAD', fontsize=lfs-2, color='red', zorder=150, ha='center', va='center', weight='bold', transform=ax.transAxes, alpha=0.8)

    # axes/spines aesthetics
    ax.set_ylim(ylims)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(True)
    
    # y scale
    if log:
        ax.set_yscale('log')

    # xticks
    xtl = [pd.to_datetime(s).strftime('%-m/%d') for s in data.index.values]
    ax.set_xticks(np.arange(len(xdata)))
    ax.set_xticklabels(xtl, rotation=90)
    ax.tick_params(pad=tpad, length=tlen)
    ax.tick_params(axis='x', labelsize=xtkfs)
    ax.tick_params(axis='y', labelsize=ytkfs)

    # x limit
    subdata = data[columns].values
    allnan = np.all(np.isnan(subdata), axis=1)
    first_nonnan = np.argwhere(allnan == False)[0][0]
    ax.set_xlim([first_nonnan - 0.5, len(subdata) - 0.75])

    # yticks
    yticks = ax.get_yticks()
    maxx = np.ceil(np.max(yticks))
    minn = 0
    if maxx < 11:
        step = 2
    elif maxx >= 11 and maxx < 45:
        step = 5
    elif maxx >= 45 and maxx < 100:
        step = 10
    else:
        step = 50
    int_range = np.arange(minn, maxx, step).astype(int)
    if not log:
        ax.set_yticks(int_range)

    # labels for data lines
    prior_ys = []
    min_dist = min_dist_factor * np.abs(np.diff(ax.get_ylim()))
    for col_idx, (column, color) in enumerate(zip(columns, colors)):
        # specify data
        ydata = data[column].values
        ydata[np.isinf(ydata)] = np.nan
        xdata = np.arange(len(ydata))

        if len(columns) > 1: # only label lines if more than one exists
            # nominally place line label at position computed as an exponentially weighted sum of the final N y-values of the data line
            ending_win = 4
            weighting = np.arange(ending_win) ** 2
            weighting = weighting / weighting.sum()
            nominal = np.nansum(ydata[-ending_win:] * weighting)
            # fix position to ensure no overlap with other data labels
            ypos = choose_y(nominal, prior_ys, min_dist=min_dist)
            prior_ys.append(ypos)
            weight = 'bold' if col_idx in bolds else None
            ax.text(xdata[-1] + 0.22, ypos, column, ha='left', va='center', color=color, fontsize=lfs, weight=weight)

    # labels for axes
    if title:
        ax.text(title_pos[0], title_pos[1], title, fontsize=tfs, weight='bold', ha='left', va='center', transform=ax.transAxes)
    ax.text(ylab_pos[0], ylab_pos[1], ylabel, fontsize=ylfs, ha='center', va='center', transform=ax.transAxes)

    # convert to image in numpy array
    #canvas.draw()
    #s, (width, height) = canvas.print_to_buffer()
    #arr_img = np.fromstring(s, np.uint8).reshape((height, width, 4))

    # save image
    path = os.path.join(out_dir, f'{name}.{fmt}')
    pl.savefig(path)

    pl.close(fig)
    return path

def generate_html(paths, pixel_width=500):
    
    img_tags = []
    for path in paths:
        width = pixel_width
        height = int(round(fig_size[1] *  pixel_width / fig_size[0]))
        img_tag = f'<div><img src="{path}" width="{width}" height="{height}"></div>'
        img_tags.append(img_tag)

    # dump images to simple webpage for quick inspection
    with open('test_webpage.html', 'w') as f:
        f.write('<html><body>\n{}\n</body></html>'.format('\n'.join(img_tags)))

