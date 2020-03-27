#!/bin/bash

cd COVID-19
git pull origin master
cd ..
python3 scrape.py