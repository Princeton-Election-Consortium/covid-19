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

# In general, numeric values can be adjusted here as desired, unless comments specify otherwise

# Aesthetic parameters
fig_size = (18, 11)
size_scale = fig_size[0] / 18 # do not adjust; ensures that fonts etc remain reasonable if fig_size is changed
ax_box = [0.24, 0.15, 0.6, 0.8]
ax_box_simple = [0.08, 0.17, 0.82, 0.75]

# font sizes
tfs = 25 * size_scale # title font size
lfs = 25 * size_scale# series label font size
ylfs = 30 * size_scale # ylabel font size
xtkfs = 25 * size_scale # xtick font size
ytkfs = 30 * size_scale # ytick font size

# ticks
tpad = 7 * size_scale
tlen = 10 * size_scale

# label positions
title_pos = (0.05, 0.94)
ylab_pos = (-0.245, 0.5)
min_dist = 0.04
data_label_x = 0.38

# axes limits
ylims = (0.0, None)

# line formatting
sns_cols = [(0, 0, 0)] + sns.color_palette('deep')
data_linewidth = 4 * size_scale
data_line_color = 'darkslateblue'


def choose_y(pos, priors, ax, min_dist=min_dist, inc=0.01):
    """Adjust a y coordinate such that it stays a min distance from list of other coordinates

    min_dist in axes coordinates
    pos and priors in data coordinates
    """
    
    # setup transform functions
    axes_to_data = (ax.transAxes + ax.transData.inverted())
    data_to_axes = (axes_to_data.inverted())
    def dat2ax_delta(delta, y):
        """Convert a delta on y axis at position y, from data to axes coords.
        Difference from pos to pos+delta (as opposed to 0+delta) needed only for log scale where position on y axis influences relative scale
        """
        p1 = data_to_axes.transform((0, y))[1]
        p2 = data_to_axes.transform((0, y + delta))[1]
        return p2 - p1

    def get_dif(pos, priors):
        """As best ypos is searched for, distances to other labels are computed in axes coords so they can be compared to min_dist also in axes_coords, especially important when log scale because position on scale determines size of delta

        This function accepts all in data coordinates
        """
        dif = pos - priors
        dif = np.array([dat2ax_delta(i, pos) for i in dif])
        return dif
    
    if len(priors) == 0:
        return pos
    priors = np.array(priors)
    
    # run through a range of positions and compute the closest label at each one
    possible = np.arange(0, 1, inc) # span entire axes coordinates
    mins = []
    for poss in possible:
        poss = axes_to_data.transform((0, poss))[1] # convert temporarily to data coordinates
        closest = np.min(np.abs(get_dif(poss, priors))) # distance of the closest other label if we place at poss
        mins.append(closest)
    mins = np.array(mins)

    # find positions where min meets distance criteria, then choose closest one
    meets_dist_critera = mins > min_dist
    contenders = possible[meets_dist_critera]
    # back to data coords to find option that is closest to originally desired value
    contenders = np.array([axes_to_data.transform((0, i))[1] for i in contenders])
    best = np.argmin(np.abs(contenders - pos))
    pos = contenders[best]
    
    return pos

def generate_plot(filename, columns, title='', ylabel='', log=False, bolds=[], min_date=None, name='plot', out_dir='images', fmt='png', runaway_zone=False, simplified=False, simp_fs_mult=1):
    """Generate plot and return path to saved figure image

    filename : relative path to csv with values to plot
    columns : str of list thereof of column names to plots
    title : optional string at title on plot
    ylabel : optional string as ylabel on plot
    log : use log scale on y axis
    bolds : list of indices parallel to `columns` whose label to bold
    min_date : minimum date to plot

    The parameters for the function are limited to those that will likely be changed on a plot-to-plot basis. The remainder of the parameters for plotting are specified at the top of this `displays` module.
    """

    # process params
    if not isinstance(columns, (list, np.ndarray)):
        columns = [columns]
    if not title and len(columns) == 1:
        title = columns[0]

    # load data
    data = pd.read_csv(filename, index_col=0)

    new_columns = []
    for col in columns:
        sdat = data[col].values
        if np.sum(sdat) == 0:
            columns.remove(col)
            continue
        isnan = np.isnan(sdat)
        if len(np.argwhere(isnan == False)) == 0:
            columns.remove(col)
            continue
        new_columns.append(col)
    columns = new_columns

    # process data for display purposes
    for col in columns:
        sdat = data[col].values
        isnan = np.isnan(sdat)
        first_nonnan = np.argwhere(isnan == False)[0][0]
        sdat[:first_nonnan + 3] = np.nan
        data[col] = sdat
    if min_date is not None:
        data = data[pd.to_datetime(data.index) >= min_date]
    data[data==0] = np.nan

    # setup axes
    fig = pl.figure(figsize=fig_size)
    canvas = FigureCanvas(fig)

    ax = None
    if simplified:
        ax = fig.add_axes(ax_box_simple)
    else:
        ax = fig.add_axes(ax_box) 

    # plot data
    colors = sns_cols[:len(columns)]
    last_ys = []
    for col_idx, (column, color) in enumerate(zip(columns, colors)):
        # specify data
        ydata = data[column].values
        last_ys.append(ydata[-1]) # for labels later on
        ydata[ydata > 20] = np.nan
        ydata[np.isinf(ydata)] = np.nan
        xdata = np.arange(len(ydata))

        # aesthetic prep
        data_line_color = "black"
        if len(columns) > 1:
            data_line_color = color
        lw = data_linewidth
        if col_idx in bolds:
            lw *= 2

        # plot line
        ax.plot(xdata, ydata, lw=lw, color=data_line_color)

    # plot reference data
    if runaway_zone:
        ref = 3
        ax.axhspan(0, ref, color='lightcoral', alpha=0.2, lw=0)
        xpos = 0.25 if simplified else 0.2
        ax.text(xpos, .04, 'RUNAWAY SPREAD', fontsize=(lfs-2)*simp_fs_mult if simplified else (lfs-2), color='red', zorder=150, ha='center', va='center', weight='bold', transform=ax.transAxes, alpha=0.8)

    # axes/spines aesthetics
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(True)
    
    # y scale
    if log:
        ax.set_yscale('log')
    if not log:
        ax.set_ylim(ylims)

    # xticks
    xtl = [pd.to_datetime(s).strftime('%-m/%d') for i, s in enumerate(data.index.values) if i % 3 == 0]
    ax.set_xticks(np.arange(0, len(xdata), 3))
    if simplified:
        ax.set_xticklabels(xtl, rotation=70)
    else:
        ax.set_xticklabels(xtl, rotation=0)

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

    # tick params
    ax.tick_params(pad=tpad, length=tlen)
    ax.tick_params(axis='x', labelsize=xtkfs * simp_fs_mult if simplified else xtkfs)
    ax.tick_params(axis='y', labelsize=ytkfs * simp_fs_mult if simplified else ytkfs)

    # labels for data lines
    #descending = np.argsort(last_ys[1:])[::-1] + 1
    #order = np.append(0, descending)
    order = np.argsort(last_ys)[::-1]
    is_bold = np.zeros(len(columns))
    is_bold[bolds] = 1
    columns_reordered = np.array(columns)[order]
    colors_reordered = np.array(colors)[order]
    is_bold_reordered = is_bold[order]
    prior_ys = []
    for col_idx, (column, color, is_bold) in enumerate(zip(columns_reordered, colors_reordered, is_bold_reordered)):
        # specify data
        ydata = data[column].values
        ydata[np.isinf(ydata)] = np.nan
        xdata = np.arange(len(ydata))

        if len(columns) > 1: # only label lines if more than one exists

            # nominally place line label at position computed as an exponentially weighted sum of the final N y-values of the data line
            #ending_win = 4
            #weighting = np.arange(ending_win) ** 5
            #weighting = weighting / weighting.sum()
            #nominal = np.nansum(ydata[-ending_win:] * weighting)

            # or just last data point that isnt nan
            nonnan = ydata[~np.isnan(ydata)]
            nominal = nonnan[-1] if len(nonnan) else 0

            # fix position to ensure no overlap with other data labels
            ypos = choose_y(nominal, prior_ys, ax)
            prior_ys.append(ypos)
            weight = 'bold' if is_bold else None
            if not simplified or column == "US" or column == "World":
                ax.text(xdata[-1] + data_label_x, ypos, column, ha='left', va='center', color=color, fontsize=lfs * simp_fs_mult if simplified else lfs, weight=weight)

    # labels for axes
    if title:
        ax.text(title_pos[0], title_pos[1], title, fontsize=tfs, weight='bold', ha='left', va='center', transform=ax.transAxes)
    ax.text(ylab_pos[0], ylab_pos[1], ylabel, fontsize=ylfs, ha='center', va='center', transform=ax.transAxes)

    # convert to image in numpy array
    #canvas.draw()
    #s, (width, height) = canvas.print_to_buffer()
    #arr_img = np.fromstring(s, np.uint8).reshape((height, width, 4))

    # save image
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f'{name}.{fmt}')
    pl.savefig(path)

    pl.close(fig)
    return path

def generate_html(paths, pixel_width=200):
    
    img_tags = []
    for path in paths:
        width = pixel_width
        height = int(round(fig_size[1] *  pixel_width / fig_size[0]))
        img_tag = f'<div><img src="{path}" width="{width}" height="{height}"></div>'
        img_tags.append(img_tag)

    # dump images to simple webpage for quick inspection
    with open('test_webpage.html', 'w') as f:
        f.write('<html><body>\n{}\n</body></html>'.format('\n'.join(img_tags)))

