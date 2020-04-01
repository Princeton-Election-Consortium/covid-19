import sys, datetime
import numpy as np
import pandas as pd
import csv

ALL_STATES = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut","Delaware","Florida","Georgia","Hawaii","Idaho","Illinois", "Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming","DC"]
ALL_COUNTRIES = ['Canada', 'US', 'China', 'Italy', 'Spain', 'South Korea', 'Australia', 'Germany', 'France', 'Japan', 'Iran', 'UK', 'World']
ALL_US_REGIONS = {'Pacific': ['Washington', 'Oregon', 'California'],
                  'Rockies': ['Nevada', 'Idaho', 'Montana', 'Wyoming', 'Utah', 'Colorado'],
                  'Southwest': ['Arizona', 'New Mexico', 'Oklahoma', 'Texas'],
                  'Midwest': ['North Dakota', 'South Dakota', 'Nebraska', 'Kansas', 'Minnesota', 'Iowa', 'Missouri', 'Wisconsin', 'Illinois', 'Indiana', 'Ohio', 'Michigan'],
                  'Northeast': ['Massachusetts', 'Rhode Island', 'Connecticut', 'Vermont', 'New Hampshire', 'Maine', 'Pennsylvania', 'New Jersey', 'New York'],
                  'Southeast': ['Arkansas', 'Louisiana', 'Mississippi', 'Alabama', 'Tennessee', 'Kentucky', 'North Carolina', 'South Carolina', 'Georgia', 'Florida'] + ['Virginia', 'West Virginia', 'Maryland', 'Delaware', 'DC'], # 2nd list is 'mid-atlantic'
                  # below are the groups in which southeast is split into southeast- and mid-atlantic
                  'Southeast-': ['Arkansas', 'Louisiana', 'Mississippi', 'Alabama', 'Tennessee', 'Kentucky', 'North Carolina', 'South Carolina', 'Georgia', 'Florida'],
                  'Mid-Atlantic': ['Virginia', 'West Virginia', 'Maryland', 'Delaware', 'DC'], 
        }

def scrape_regional_data(region="new jersey", 
                         region_type="state",
                         var_to_track="Deaths",
                         start_date=datetime.date(2020, 1, 25),
                         data_src_template="COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/{datestr}.csv"):

    """Scrape data for a given region and store in local csv file
    
    Parameters
    ----------
    region : name of region, e.g. "new jersey"
    region_type : "state" or "country"
    var_to_track : e.g. "Deaths" / "Confirmed" / "Recovered"
    start_date : datetime date object, e.g. datetime.date(2020, 1, 1)
    data_src_template : str template for data source files

    Returns
    -------
    regional_data : pd Series with index of dates and values of var_to_track
    """

    region_type_dict = {"state": "Province_State",
                        "country": "Country_Region"}

    column_rename = {'Province/State': 'Province_State',
                     'Country/Region': 'Country_Region'}

    value_relabel = {'Mainland China': 'China',
                     'Korea, South': 'South Korea',
                     'Republic of Korea': 'South Korea',
                     'Iran (Islamic Republic of)': 'Iran',
                     'District of Columbia': 'DC',
                     'United Kingdom': 'UK'}

    if not isinstance(region, list):
        region = [region]

    region = [r.lower() for r in region]
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
        data.replace(value_relabel, inplace=True)

        # collect only rows from region of interest
        is_region = data[region_type].str.lower().isin(region)
        rows = data[is_region]
        if 'world' in region:
            rows = data
            #rows = data[data['Country_Region'].str.lower() != 'china']

        # collect values of relevant variable (e.g. deaths)
        values = rows[var_to_track].values
        total = np.nansum(values)

        # store values
        dates[day] = np.datetime64(date)
        totals[day] = total

    result = pd.Series(totals, index=dates)
    return result

def scrape_all_regions(**kw):
    """Run scrape_regional_data on all states and return merged DataFrame
    """
    series_states = {state:scrape_regional_data(state, **kw) for state in ALL_STATES}
    data_states = pd.DataFrame(series_states)

    series_countries = {cou:scrape_regional_data(cou, region_type='country', **kw) for cou in ALL_COUNTRIES}
    data_countries = pd.DataFrame(series_countries)
    
    series_us_regions = {usr:scrape_regional_data(usr_contents, **kw) for usr,usr_contents in ALL_US_REGIONS.items()}
    data_us_regions = pd.DataFrame(series_us_regions)

    return pd.concat([data_states, data_countries, data_us_regions], axis=1)
