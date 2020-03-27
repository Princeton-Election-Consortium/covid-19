#!/usr/bin/env python3
#
# Author: Lucas Manning

import sys, datetime, os
import requests
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def main():
    to_track = "Deaths"
    region = "New Jersey"
    #
    # uncomment this line if you want to track US instead of a specific state
    # type_to_track = ("Country_Region", "Country/Region")
    #
    type_to_track = ("Province_State", "Province/State")

    start_date = datetime.date(2020, 3, 10)
    end_date = datetime.date.today()
    time_delta = end_date - start_date

    # grabbing and calculating totals for given region    
    totals = [0] * time_delta.days
    for days_since_start in range(time_delta.days):
        date = start_date + datetime.timedelta(days=days_since_start)
        
        with open( f"COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/{date.strftime('%m-%d-%Y')}.csv", "r",  encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if date > datetime.date(2020, 3, 21):
                    if row[type_to_track[0]] == region:
                        totals[days_since_start] += int(row[to_track]) if row[to_track] != "" else 0
                else:
                    if row[type_to_track[1]] == region:
                        totals[days_since_start] += int(row[to_track]) if row[to_track] != "" else 0

    # calculating days to double the total cases
    days_to_double = [0] * time_delta.days 
    for i, total in enumerate(totals):
        j = i - 1
        days_to_double[i] = 0
        while j > 0:
            if totals[j] <= 0.5 * totals[i]:
                days_to_double[i] = i - j
                break
            j -= 1

    # calculating percentage change in over three days
    percent_change = [0] * time_delta.days 
    for i, total in enumerate(totals):
        if i >= 3:
            percent_change[i] = total / totals[i-3]
        else:
            percent_change[i] = 0


    # generating graphics
    # NOTE: Ben you can probably just tear this stuff out and write your own from here forward. 
    # just really basic matplotlib stuff here

    x_values = [start_date + datetime.timedelta(days=days_since_start) for days_since_start in range(time_delta.days)]
    fig, ax1 = plt.subplots()
    plt.title(f"{to_track} Time to Double {region}")

    # this stuff is all related to sam wanting to "floor doubling rate at 3"
    # I think he wants to remove this now
    days_to_double = [x if x > 3 else 3 for x in days_to_double]
    ticks = list(range( 3, 23, 2 ))
    ticks[0] = "<=3"
    # ==================

    ax1.set_ylabel("Doubling time (days)"); 
    ax1.set_yticks(range(3, 23, 2))
    ax1.set_yticklabels(ticks)
    ax1.set_ylim([0,10])
    color = 'tab:red'
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(axis='y')

    ax1.plot(x_values, days_to_double, color=color)

    color = 'tab:blue'
    ax2 = ax1.twinx()
    ax2.set_ylabel(to_track); 
    ax2.set_yticks([2**x for x in range(15)])
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.plot(x_values, percent_change, color=color)

    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))

    fig.tight_layout()
    fig.autofmt_xdate()

    plt.savefig(f"{region + to_track}.png")

    return 0
        

if __name__ == "__main__":
    exit(main())
