#!/bin/bash

# Pull new data
git pull origin master
git submodule foreach git pull origin master

# Run pipeline
python3 main.py deaths
python3 main.py confirmed

