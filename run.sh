#!/bin/bash

# Pull new data
git pull origin master
cd COVID-19
git pull origin master
cd ..

# Run pipeline
python3 main.py deaths
python3 main.py confirmed

# copy output folders
cp images/* "/web/www/data/covid-19/today"
mkdir "/web/www/data/covid-19/$(date +"%d-%m-%Y")"
cp images/* "/web/www/data/covid-19/$(date +"%d-%m-%Y")"
cp data/* "/web/www/data/covid-19/"
