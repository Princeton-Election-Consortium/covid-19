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
from calculations import calculate, compute_top_n, calculation_descriptions
from displays import generate_plot, create_html

# Parameters
var_to_track = 'Deaths'
calculation_kind = 'doubling_time'
scraped_data_filename = f'data/scraped_data-{var_to_track}.csv'
calculated_filename = f'data/{calculation_kind}-{var_to_track}.csv'

# Setup
os.makedirs('data', exist_ok=True)
os.makedirs('images', exist_ok=True)

## Step 1: scrape and save to file
data = scrape_all_regions(var_to_track=var_to_track)
data.to_csv(scraped_data_filename)

## Step 2: run calculations
doubling_time = calculate(calculation_kind, scraped_data_filename)
doubling_time.to_csv(calculated_filename)

## Step 3: generate plots
columns = compute_top_n(calculated_filename, 50)
imgs, htmls = [], []
for column in columns:
    img, html = generate_plot(calculated_filename, column,
            ylabel=calculation_descriptions[calculation_kind])
    imgs.append(img)
    htmls.append(html)

## Step 4: generate html
create_html(imgs, htmls)
