#!/usr/bin/env python3
#
# Author: Lucas Manning

import sys, datetime
import numpy as np
import pandas as pd
import csv

ALL_STATES = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut","Delaware","Florida","Georgia","Hawaii","Idaho","Illinois", "Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"]

def scrape_regional_data(region="new jersey", 
                         region_type="state",
                         var_to_track="Deaths",
                         start_date=datetime.date(2020, 3, 10),
                         data_src_template="COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/{datestr}.csv"):

    """Scrape data for a given region and store in local csv file
    
    Parameters
    ----------
    region : name of region, e.g. "new jersey"
    region_type : "state" or "country"
    var_to_track : e.g. "Deaths"
    start_date : datetime date object, e.g. datetime.date(2020, 1, 1)

    Returns
    -------
    regional_data : pd Series with index of dates and values of var_to_track
    """

    region_type_dict = {"state": "Province_State",
                        "country": "Country_Region"}

    column_rename = {'Province/State': 'Province_State',
                     'Country/Region': 'Country_Region'}

    region = region.lower()
    region_type = region_type.lower()
    region_type = region_type_dict[region_type]

    end_date = datetime.date.today()
    time_delta = end_date - start_date
    n_days = time_delta.days

    # grab and calculate totals for given region    
    dates = np.zeros(n_days, dtype='datetime64[s]')
    totals = np.zeros(n_days)

    for day in range(n_days):
        # specify day of interest and relevant data file
        date = start_date + datetime.timedelta(days=day)
        datestr = date.strftime('%m-%d-%Y')
        data_src = data_src_template.format(datestr=datestr)

        # open data file
        data = pd.read_csv(data_src)

        # clean up
        data.rename(column_rename, axis=1, inplace=True)

        # collect only rows from region of interest
        is_region = data[region_type].str.lower() == region
        rows = data[is_region]

        # collect values of relevant variable (e.g. deaths)
        values = rows[var_to_track].values
        total = np.nansum(values)

        # store values
        dates[day] = np.datetime64(date)
        totals[day] = total

    result = pd.Series(totals, index=dates)
    return result

def scrape_all_regions():
    """Run scrape_regional_data on all states and return merged DataFrame
    """
    series = {state:scrape_regional_data(state) for state in ALL_STATES}
    data = pd.DataFrame(series)
    return data
