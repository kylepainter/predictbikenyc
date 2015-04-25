#!/bin/bash
# Preprocessing code
#
# This is code for preprocessing the data, creating a prediction index, 
# and drawing graphs.
# If not using this bash script, the files have to be run in the following order:

python stationdatacompilation.py
python weathercompilation.py
python bikedatacompilation.py
python createpredictionfiles.py
python googlecomparisongraphs.py
python zones.py
python rain.py
