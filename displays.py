import matplotlib.pyplot as pl
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.transforms import blended_transform_factory as blend
from imageio import imwrite
import pandas as pd
import numpy as np
import datetime
import mpld3
    
# Aesthetic parameters
fig_size = (16, 9)
ax_box = [0.25, 0.1, 0.65, 0.8]

tfs = 25 # title font size
lfs = 20 # label font size
tkfs = 15 # tick font size

title_pos = (0.05, 0.94)
ylab_pos = (-0.2, 0.5)

ylims = (0.0, None)
n_yticks = 8

cmap = pl.cm.cubehelix

data_line_kw = dict(
                    linewidth = 4,
                    color = 'darkslateblue',
                    )

ref_line_kw = dict(color = 'black',
                   linewidth = 1.5,
                   dashes = [4, 2],
                  )

def choose_y(pos, priors, min_dist=0.25, inc=0.01):
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

def generate_plot(filename, columns, title='', ylabel=''):

    # process params
    if not isinstance(columns, list):
        columns = [columns]
    if not title and len(columns) == 1:
        title = columns[0]

    # load data
    data = pd.read_csv(filename, index_col=0)

    # setup axes
    fig = pl.figure(figsize=fig_size)
    canvas = FigureCanvas(fig)
    ax = fig.add_axes(ax_box) 

    # plot data
    colors = cmap(np.linspace(0.05, 0.76, len(columns)))
    prior_ys = []
    for column, color in zip(columns, colors):
        # specify data
        ydata = data[column].values
        ydata[np.isinf(ydata)] = np.nan
        xdata = np.arange(len(ydata))

        # aesthetic prep
        if len(columns) > 1:
            data_line_lw['color'] = color

        # plot line
        ax.plot(xdata, ydata, **data_line_kw)

        # label
        if len(columns) > 1:
            ypos = choose_y(ydata[-1], prior_ys)
            prior_ys.append(ypos)
            ax.text(xdata[-1] + 0.1, ypos, column, ha='left', va='center', color=color, fontsize=lfs)

    # plot reference data
    ax.axhline(3, zorder=101, **ref_line_kw)

    # axes/spines aesthetics
    ax.set_ylim(ylims)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(True)

    # xticks
    xtl = [pd.to_datetime(s).strftime('%-m/%d') for s in data.index.values]
    ax.set_xticks(np.arange(len(xdata)))
    ax.set_xticklabels(xtl, rotation=90)
    ax.tick_params(pad=11, length=10, labelsize=tkfs)

    # yticks
    yticks = ax.get_yticks()
    maxx = np.ceil(np.max(yticks))
    minn = 1 #np.floor(np.min(yticks))
    int_range = np.arange(minn, maxx + 1).astype(int)
    if len(int_range) > n_yticks:
        step = int(np.round(len(int_range) / n_yticks))
    else:
        step = 1
    ax.set_yticks(int_range[::step])

    # labels
    ax.text(title_pos[0], title_pos[1], title, fontsize=tfs, weight='bold',
            ha='left', va='center', transform=ax.transAxes)
    ax.text(ylab_pos[0], ylab_pos[1], ylabel, fontsize=lfs, ha='center', va='center', transform=ax.transAxes)

    # shading boxes
    ax.axhspan(0, 3, color='white', alpha=0.5, lw=0, zorder=100)

    # convert to image, html
    canvas.draw()
    s, (width, height) = canvas.print_to_buffer()
    img = np.fromstring(s, np.uint8).reshape((height, width, 4))
    html = mpld3.fig_to_html(fig)
    pl.close(fig)

    return img, html

def create_html(imgs, htmls):

    if not isinstance(htmls, list):
        imgs = [imgs]
        htmls = [htmls]

    # Option 1: use htmls wth interactive matplotlib; may be buggy
    #with open('test_webpage.html', 'w') as f:
    #    f.write('<html><body>\n{}\n</body></html>'.format('\n\n'.join(htmls)))

    # Option 2: use pngs
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
