import matplotlib.pyplot as pl
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.transforms import blended_transform_factory as blend
import seaborn as sns
from imageio import imwrite
import pandas as pd
import numpy as np
import datetime
import mpld3
    
# Aesthetic parameters
fig_size = (17, 10)
ax_box = [0.24, 0.15, 0.63, 0.8]

tfs = 25 # title font size
lfs = 25 # series label font size
ylfs = 30 # ylabel font size
xtkfs = 25 # xtick font size
ytkfs = 30 # ytick font size

title_pos = (0.05, 0.94)
ylab_pos = (-0.24, 0.5)

ylims = (0.0, None)
n_yticks = 8

sns_cols = [(0, 0, 0)] + sns.color_palette('deep')

data_linewidth = 4
data_line_kw = dict(
                    color = 'darkslateblue',
                    )

ref_line_kw = dict(color = 'black',
                   linewidth = 1.5,
                   dashes = [4, 2],
                  )

def choose_y(pos, priors, min_dist=0.3, inc=0.01):
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

def generate_plot(filename, columns, title='', ylabel='', log=False, bolds=[], min_date=None):
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
            data_line_kw['color'] = color
        lw = data_linewidth
        if col_idx in bolds:
            lw *= 2

        # plot line
        ax.plot(xdata, ydata, lw=lw, **data_line_kw)

    # plot reference data
    #ax.axhline(3, zorder=101, **ref_line_kw)
    #pct90 = np.nanpercentile(data[columns].values, 90) # global 90th percentile values
    pct90 = 3
    ax.axhspan(0, pct90, color='lightgrey', alpha=0.35, lw=0)

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
    ax.tick_params(pad=7, length=10)
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
    if maxx < 10:
        step = 2
    elif maxx >= 10 and maxx < 45:
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
    min_dist = 0.06 * np.abs(np.diff(ax.get_ylim()))
    for col_idx, (column, color) in enumerate(zip(columns, colors)):
        # specify data
        ydata = data[column].values
        ydata[np.isinf(ydata)] = np.nan
        xdata = np.arange(len(ydata))

        if len(columns) > 1:
            ending_win = 4
            weighting = np.arange(ending_win) ** 2
            weighting = weighting / weighting.sum()
            nominal = np.nansum(ydata[-ending_win:] * weighting)
            ypos = choose_y(nominal, prior_ys, min_dist=min_dist)
            prior_ys.append(ypos)
            weight = 'bold' if col_idx in bolds else None
            ax.text(xdata[-1] + 0.22, ypos, column, ha='left', va='center', color=color, fontsize=lfs, weight=weight)

    # labels for axes
    if title:
        ax.text(title_pos[0], title_pos[1], title, fontsize=tfs, weight='bold', ha='left', va='center', transform=ax.transAxes)
    ax.text(ylab_pos[0], ylab_pos[1], ylabel, fontsize=ylfs, ha='center', va='center', transform=ax.transAxes)

    # convert to image, html
    canvas.draw()
    s, (width, height) = canvas.print_to_buffer()
    img = np.fromstring(s, np.uint8).reshape((height, width, 4))
    #html = mpld3.fig_to_html(fig) # Quite buggy so on hold
    pl.close(fig)

    return img#, html

def create_html(imgs, htmls=None):

    if not isinstance(imgs, list):
        imgs = [imgs]
        htmls = [htmls]

    # Option 1: generate pngs from image data
    img_tags = []
    for idx, img in enumerate(imgs):
        fname = f'images/{idx}.png'
        imwrite(fname, img)
        width = fig_size[0] * 40
        height = fig_size[1] * 40
        img_tag = f'<div><img src="{fname}" width="{width}" height="{height}"></div>'
        img_tags.append(img_tag)
    with open('test_webpage.html', 'w') as f:
        f.write('<html><body>\n{}\n</body></html>'.format('\n'.join(img_tags)))

    # Option 2: use htmls wth interactive matplotlib; quite buggy
    #with open('test_webpage.html', 'w') as f:
    #    f.write('<html><body>\n{}\n</body></html>'.format('\n\n'.join(htmls)))

