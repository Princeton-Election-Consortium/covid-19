"""
Run one iteration of the workflow:
    - scrape new data from JHU database
    - compute relevant metrics
    - generate plots
    - convert plots to web-friendly format

This script will be run once per day(?) using a cron job on the PEC server.
It is run from using the run.sh bash script which first pulls down new data.
"""

import os
from scrape import scrape_all_regions
from calculations import compute_fold_change, compute_top_n
from displays import generate_foldchange_plot, create_html

# Parameters
var_to_track = 'Deaths'
scraped_data_filename = f'data/scraped_data-{var_to_track}.csv'
foldchange_filename = f'data/fold_change-{var_to_track}.csv'

# Setup
os.makedirs('data', exist_ok=True)
os.makedirs('images', exist_ok=True)

## Step 1: scrape and save to file
data = scrape_all_regions(var_to_track=var_to_track)
data.to_csv(scraped_data_filename)

## Step 2: run calculations
fold_change = compute_fold_change(scraped_data_filename)
fold_change.to_csv(foldchange_filename)

## Step 3: generate plots
# Fold change with top death
columns = compute_top_n(scraped_data_filename, n=5)
img0, html0 = generate_foldchange_plot(foldchange_filename, columns,
                        title='Top 5 states\nby # of deaths')
# Fold change with top fold change
columns = compute_top_n(foldchange_filename, n=5)
img1, html1 = generate_foldchange_plot(foldchange_filename, columns,
                        title='Top 5 states\nby fold increase')

## Step 4: generate html
imgs = [img0, img1]
htmls = [html0, html1]
create_html(imgs, htmls)
