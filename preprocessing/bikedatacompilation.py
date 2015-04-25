import pandas as pd
from numpy import sqrt
import numpy as np
import os
import warnings
warnings.simplefilter("ignore", category = FutureWarning) # eliminates pandas future warning for pickled df

project_location = '/home/vagrant/projectcode/predictbikenyc'

# bikeweather.file is 1.2GB and not needed for deployed website
# so it is not accessible via github. It can, however, be produced
# using this script.
path_for_bikeweather = '/home/vagrant/projectcode/bikeweather.file'

# citibike data is too large to place in github; can be found here: 
# http://www.citibikenyc.com/system-data
files = ['201405-CitiBike-tripdata.csv',
 '201410-CitiBike-tripdata.csv',
 '201407-CitiBike-tripdata.csv',
 '201411-CitiBike-tripdata.csv',
 '201409-CitiBike-tripdata.csv',
 '201404-CitiBike-tripdata.csv',
 '201406-CitiBike-tripdata.csv',
 '201408-CitiBike-tripdata.csv',
 '201412-CitiBike-tripdata.csv']

bikedata_directory = "/home/vagrant/projectcode/data/"

path_for_df = project_location + '/app/static/dataframes/'
weather = pd.load(path_for_df + 'weather.file')

def main():
#    files = [f for f in os.listdir(bikedata_directory) if "CitiBike-tripdata" in f ]
    j = 0
    for f in files:  
        bikedf = pd.read_csv(bikedata_directory + f)
        if j == 0:
            bike = transform_bike_data(bikedf)
            j = 1
        else:
            bike = bike.append(transform_bike_data(bikedf))

    bikeweather = pd.merge(bike, weather, how='inner', on='hourdatestr')
    pd.save(bikeweather, path_for_bikeweather)


def transform_bike_data(bike):
    bikenames = [u'tripduration', u'starttime', u'stoptime', u'start_station_id', u'start_station_name', u'start_station_latitude', u'start_station_longitude', u'end_station_id', u'end_station name', u'end_station_latitude', u'end_station_longitude', u'bikeid', u'usertype', u'birth_year', u'gender']
    bike.columns = bikenames
    bike = bike.ix[bike.start_station_id != bike.end_station_id]
    bike.start_station_id = bike.start_station_id.astype(str)
    bike.end_station_id = bike.end_station_id.astype(str)
    bike['trip'] = bike.start_station_id + 'to' + bike.end_station_id

    # Subscribers are limited to 45 minutes (2700 seconds) before having to pay extra; this 
    # weeds out excessively long trips
    bike = bike[bike.tripduration < 2700]

    bike.startttime = pd.to_datetime(bike.starttime)
    bike.stoptime = pd.to_datetime(bike.stoptime)

    bike['pythdist'] = sqrt((bike.start_station_latitude - bike.end_station_latitude)**2 +\
                            (bike.start_station_longitude - bike.end_station_longitude)**2)
    bike['man_dist'] = abs(bike.start_station_latitude - bike.end_station_latitude) * 69 + abs(bike.start_station_longitude - bike.end_station_longitude) * 52.5 
    bike.starttime = pd.to_datetime(bike.starttime)
    dates = pd.DatetimeIndex(bike.starttime)
    bike['date'] = dates.date
    bike['hour'] = [int(s[11:13]) for s in np.datetime_as_string(dates)]
    bike['weekday'] = dates.weekday
    bike['hourdatestr'] = bike.hour.astype(str) + ' ' + bike.date.astype(str)
    
        # To add age to bike dataset, including filtering non-age values as negative numbers that can be easily filtered later
    # Older datafiles have birth_year as string, later have birth_year as int; handling with try/except
    try:
        bike.birth_year[bike.birth_year == "\\N"] = '2015' #"\\N" coded 2015, so age will be -1
    except:
        bike['birth_year'].fillna(2015, inplace=True) # NaN coded as 2015, so age will be -1
    bike['age'] = 2014 - bike.birth_year.astype(int)

    # Dropping information on stations except for start/stop ids. That info is in the 
    # station dataframe, and repeating it for each trip is a massive waste of memory.
    bike = bike.drop([u'start_station_latitude', u'start_station_longitude', u'start_station_name', u'end_station name', u'end_station_latitude', u'end_station_longitude', u'bikeid', u'birth_year'], 1)
    
    return bike

main()