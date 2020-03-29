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
import pandas as pd
from scrape import scrape_all_regions
from calculations import calculate, compute_top_n, c_str
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

## Step 2: run calculation
calculated = calculate(calculation_kind, scraped_data_filename)
calculated.to_csv(calculated_filename)

## Step 3: generate plots
ylab = c_str(calculation_kind, var_to_track)

# Plot 1
columns = ['US', 'New York', 'New Jersey', 'Washington', 'Ohio', 'Florida', 'DC']
bolds = [0]
img_1 = generate_plot(calculated_filename, columns, ylabel=ylab, bolds=bolds)

# Plot 2
columns = ['US', 'Pacific', 'Rockies', 'Southwest', 'Midwest', 'Southeast']
bolds = [0]
img_2 = generate_plot(calculated_filename, columns, ylabel=ylab, bolds=bolds)

# Plot 3
columns = ['World', 'Italy', 'South Korea', 'France', 'Iran', 'US', 'UK',] # 'China']
bolds = [0]
img_3 = generate_plot(calculated_filename, columns, ylabel=ylab, bolds=bolds)

## Step 4: generate html
create_html([img_1, img_2, img_3])
