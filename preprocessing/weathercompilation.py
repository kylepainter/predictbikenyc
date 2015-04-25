import pandas as pd
import numpy as np
import os
import warnings
warnings.simplefilter("ignore", category = FutureWarning) # eliminates pandas future warning for pickled df

project_location = '/home/vagrant/projectcode/predictbikenyc'

path_for_df = project_location + '/app/static/dataframes/'
data_directory = project_location + "/weatherdata/"

def main():
    files = os.listdir(data_directory)
    j = 0
    for f in files:
        weatherdf = pd.read_csv(data_directory + f)
        if j == 0:
            weather = transform_weather_data(weatherdf)
            j = 1
        else:
            weather = weather.append(transform_weather_data(weatherdf))
    weather = weather.set_index('datetime')

    pd.save(weather, path_for_df + "weather.file")


def transform_weather_data(weather):

    #transforms data from csv into date and hour format amenable to merging with bike data
    weather.Date = weather.Date.astype('str')
    weather.Time = weather.Time.astype('str')
    year = weather.Date.str.slice(0, 4)
    month = weather.Date.str.slice(4, 6)
    date = weather.Date.str.slice(6, 8)
    time = weather.Time.str.rstrip()
    time = list(time)
    thistime = []
    for t in time:
        if len(t) == 1: thistime.append('000' + t)
        elif len(t) == 2: thistime.append('00' + t)
        elif len(t) == 3: thistime.append('0' + t)
        else: thistime.append(t)
    weather['datetime'] = pd.to_datetime(pd.TimeSeries(year+month+date+thistime))
    weather['pandadate'] = pd.to_datetime(weather.Date)
    wdates = pd.DatetimeIndex(weather.datetime)
    weather['date'] = wdates.date
    weather['hour'] = [int(s[11:13]) for s in np.datetime_as_string(wdates)]
    weather['hourdatestr'] = weather.hour.astype(str) + ' ' + weather.date.astype(str)

    #changing rain data to numerical; note that trace rain ("T") defined as zero
    weather.HourlyPrecip[weather.HourlyPrecip == ' '] = 0
    weather.HourlyPrecip[weather.HourlyPrecip == '  T'] = 0
    weather.HourlyPrecip = weather.HourlyPrecip.astype(float)

    #selecting only desired columns
    newweath = weather[['datetime','hourdatestr', 'HourlyPrecip','WindDirection', 'WindSpeed', 'DryBulbFarenheit']][weather.Time.str.endswith('51')]

    return newweath

main()