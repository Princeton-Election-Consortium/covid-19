## Imports
import matplotlib.pyplot as pl
import mpld3

xdata, ydata = np.arange(10), np.random.random(10)

# Aesthetic parameters
fig_size = (5, 2)

data_line_kw = dict(color = 'darkslateblue',
                    linewidth = 4,
                    )

ref_line_kw = dict(color = 'grey',
                   linewidth = 2,
                    )

# Plot relevant data
fig, ax = pl.subplots(figsize=fig_size)
ax.plot(xdata, ydata, **data_line_kw)

# Convert to html
html = mpld3.fig_to_html(fig)

# Save out html

##
