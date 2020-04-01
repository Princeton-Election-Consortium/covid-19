"""
Run one iteration of the workflow:
    - scrape new data from JHU database
    - compute relevant metrics
    - generate plots
    - convert plots to web-friendly format

This script will be run once per day(?) using a cron job on the PEC server.
It is run using the run.sh bash script which first pulls down new data.
"""

import os, sys
import pandas as pd
from scrape import scrape_all_regions
from calculations import calculate, compute_top_n, c_str
from displays import generate_plot, generate_html

# Coarsely parse script arguments
args = sys.argv
if 'Deaths' in args or 'death' in args:
    var_to_track = 'Deaths'
elif 'Confirmed' in args or 'confirmed' in args:
    var_to_track = 'Confirmed'
else:
    var_to_track = 'Deaths'

# Default parameters
calculation_kind = 'doubling_time' # doubling_time / fold_change
show_n_days = 25
scraped_data_filename = f'data/scraped_data-{var_to_track}.csv'
calculated_filename = f'data/{calculation_kind}-{var_to_track}.csv'
runaway_zone = calculation_kind == 'doubling_time'
log = calculation_kind == 'fold_change'
output_reverse_csv = True

## Step 1: scrape and save to file
data = scrape_all_regions(var_to_track=var_to_track)
os.makedirs('data', exist_ok=True)
data.to_csv(scraped_data_filename)

## Step 2: run calculation
calculated = calculate(calculation_kind, scraped_data_filename)
calculated.to_csv(calculated_filename)

if output_reverse_csv:
    calculated_reversed = calculated.sort_index(axis=0, ascending=False)
    calculated_reversed_filename = f'data/{calculation_kind}-{var_to_track}-reversed.csv'
    calculated_reversed.to_csv(calculated_reversed_filename)


## Step 3: generate and save plots
ylab = c_str(calculation_kind, var_to_track)
min_date = pd.Timestamp.today() - pd.to_timedelta(show_n_days, unit='D')
min_date_states = max(min_date, pd.to_datetime('2020-3-6'))

# Plot 1
name_1 = f'{calculation_kind}_{var_to_track}_US-states'
columns = ['US', 'New York', 'New Jersey', 'Washington', 'Ohio', 'Florida']
path_1 = generate_plot(calculated_filename,
                       columns,
                       ylabel=ylab,
                       bolds=[0],
                       log=log,
                       runaway_zone=runaway_zone,
                       min_date=min_date_states,
                       name=name_1)

# Plot 2
name_2 = f'{calculation_kind}_{var_to_track}_US-regions'
columns = ['US', 'Midwest', 'Northeast', 'Rockies', 'Southeast', 'Southwest', 'Pacific']
path_2 = generate_plot(calculated_filename,
                       columns,
                       ylabel=ylab,
                       bolds=[0],
                       log=log,
                       runaway_zone=runaway_zone,
                       min_date=min_date_states,
                       name=name_2)

# Plot 2a
name_2a = f'{calculation_kind}_{var_to_track}_US-regions-alternate'
columns = ['US', 'Midwest', 'Northeast', 'Rockies', 'Southeast-', 'Mid-Atlantic', 'Southwest', 'Pacific']
path_2a = generate_plot(calculated_filename,
                       columns,
                       ylabel=ylab,
                       bolds=[0],
                       log=log,
                       runaway_zone=runaway_zone,
                       min_date=min_date_states,
                       name=name_2a)


# Plot 3
name_3 = f'{calculation_kind}_{var_to_track}_world'
columns = ['World', 'Italy', 'South Korea', 'France', 'Iran', 'US', 'UK']
if var_to_track == 'Confirmed':
    columns.remove('South Korea')
path_3 = generate_plot(calculated_filename,
                       columns,
                       ylabel=ylab,
                       bolds=[0],
                       log=log,
                       runaway_zone=runaway_zone,
                       min_date=min_date,
                       name=name_3)

## Step 4: generate html (as example)
generate_html([path_1, path_2, path_3])
