#!/bin/bash

# Pull new data
cd /web/covid-19
git pull origin master
cd /web/covid-19/COVID-19
git pull origin master
cd /web/covid-19

[ ! -d "/web/www/data/covid-19/$(date +"%d-%m-%Y")" ] && mkdir "/web/www/data/covid-19/$(date +"%d-%m-%Y")"

# Run pipeline
python3 main.py deaths
python3 main.py confirmed

# copy output folders
cp images/* "/web/www/data/covid-19/today"
cp images/* "/web/www/data/covid-19/$(date +"%d-%m-%Y")"
cp data/* "/web/www/data/covid-19/"
