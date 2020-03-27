"""
Run one iteration of the workflow:
    - scrape new data from JHU database
    - compute relevant metrics
    - generate plots
    - convert plots to web-friendly format

This script will be run once per day(?) using a cron job on the PEC server.
"""

from scrape import scrape_all_regions
from calculations import compute_fold_change
from displays import generate_plot

scraped_data_filename = 'scraped_data.csv'
foldchange_filename = 'fold_change.csv'

# Step 1: scrape and save to file
data = scrape_all_regions()
data.to_csv(scraped_data_filename)

# Step 2: run calculations
fold_change = compute_fold_change(scraped_data_filename)
fold_change.to_csv(foldchange_filename)

# Step 3: generate plot
html = generate_plot(foldchange_filename)
