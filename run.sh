#!/bin/bash

# Pull new data
cd COVID-19
git pull origin master
cd ..

# Run pipeline
python3 main.py deaths
python3 main.py confirmed
