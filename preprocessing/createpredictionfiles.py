import pandas as pd
import matplotlib.pyplot as plt
import warnings
import numpy as np
warnings.simplefilter("ignore", category = FutureWarning) # eliminates pandas future warning for pickled df

project_location = '/home/vagrant/projectcode/predictbikenyc'
# bikeweather.file is 1.2GB and not needed for deployed website
# so it is not accessible via github. It can, however, be produced
# by the bikeweathercompilation.py script.
path_for_bikeweather = '/home/vagrant/projectcode/bikeweather.file'

path_for_df = project_location + '/app/static/dataframes/'
bikeweather = pd.load(path_for_bikeweather)
weekday_medians_file = path_for_df + 'weekday_medians.file'
weekday_medians_no_hour_file = path_for_df + 'weekday_medians_no_hour.file'
hour_scaling_file = path_for_df + 'hour-scaling.file'
midpoint_predicted_medians_file = path_for_df + 'midpoint_medians.file'
stations = pd.load(path_for_df + 'manhattanstations.file')
stationidlist = stations.id.values

# merge bikeweather with manhattanstations to get start and end zones
# this also should have the effect of eliminating any trips with non-Manhattan endpoints
bikeweather = bikeweather.merge(stations[['id','zone']], left_on = "start_station_id", right_on = "id")
bikeweather = bikeweather.rename(columns = {'zone':'start_zone'})
bikeweather = bikeweather.drop('id', 1)
bikeweather = bikeweather.merge(stations[['id','zone']], left_on = "end_station_id", right_on = "id")
bikeweather = bikeweather.rename(columns = {'zone':'end_zone'})

def find_nearest_station(lat, lng):
    difflat = abs(stations.latitude - lat)
    difflong = abs(stations.longitude - lng)
    man_diff = (abs(difflong) * 52.5) + (abs(difflat) * 69) 
    idmin = man_diff.idxmin()
    return stations.ix[idmin].id

def estimate_time_from_man_distance(start_station, end_station):
    # ave_speed is average for all rides, regardless of hour, gender, age, or route
    ave_speed = 6.4211506442082289
    slat, slng = stations[stations.id == start_station].latitude.values, stations[stations.id == start_station].longitude.values
    elat, elng = stations[stations.id == end_station].latitude.values, stations[stations.id == end_station].longitude.values
    return abs(slat - elat) * 69 + abs(slng - elng) * 52.5 / ave_speed * 3600


def predict_using_midpoint(start_station, end_station, level = 0):
    slat, slng = stations[stations.id == start_station].latitude.values, stations[stations.id == start_station].longitude.values
    elat, elng = stations[stations.id == end_station].latitude.values, stations[stations.id == end_station].longitude.values
    midpoint_station = find_nearest_station((slat + elat)/2, (slng + elng)/2)
    # if one of the start-midpoint or midpoint-end points has no data, it splits again, and if it still finds no data,
    # estimates from man_dist and average speed
    try:
        ref_tripduration1 = weekday_medians_no_hour[start_station][midpoint_station]
    except KeyError:
        if level == 0:
            ref_tripduration1 = predict_using_midpoint(start_station, midpoint_station, level + 1)
        else:
            ref_tripduration1 = estimate_time_from_man_distance(start_station, end_station)
    try:
        ref_tripduration2 = weekday_medians_no_hour[midpoint_station][end_station]
    except KeyError:
        if level == 0:
            ref_tripduration2 = predict_using_midpoint(midpoint_station, end_station, level + 1)
        else:
            ref_tripduration2 = estimate_time_from_man_distance(start_station, end_station)
    total_duration = ref_tripduration1 + ref_tripduration2

    return total_duration

# Creating dataset for prediction, indexing median time on hour and start/end stations
dates = pd.DatetimeIndex(bikeweather.starttime)
#Prediction engine uses only weekday data
bikeweekday = bikeweather[dates.weekday < 5  ]
weekday_medians = bikeweekday.groupby(['hour', 'start_station_id', 'end_station_id']).median()['tripduration']
#keeping only times that have at least 7 data points, to reduce the effect of outliers
min_datapoints = 7
# first step of prediction: medians of trip at that time of day
weekday_medians = weekday_medians[bikeweekday.groupby(['hour', 'start_station_id', 'end_station_id']).count()['tripduration'] >= min_datapoints]
weekday_medians.save(weekday_medians_file)

# second step of prediction: medians averaged across 24 hours, scaled by speed at time of day
weekday_medians_no_hour = bikeweekday.groupby(['start_station_id', 'end_station_id']).median()['tripduration']
weekday_medians_no_hour = weekday_medians_no_hour[bikeweekday.groupby(['start_station_id', 'end_station_id']).count()['tripduration'] >= min_datapoints]
weekday_medians_no_hour.save(weekday_medians_no_hour_file)

# scaling factor based on average speed per hour across weekday dataset
hours = bikeweekday.groupby('hour')
hour_means = hours.mean()['man_dist'] / hours.mean()['tripduration'] * 3600
hour_scaling = (hour_means - np.std(hour_means) )/ np.mean(hour_means)
hour_scaling.save(hour_scaling_file)

#identify trips for which a midpoint-based analysis must be used
all_possible_trips = [(x,y) for x in stationidlist for y in stationidlist if x != y]
wmnh_trips = [tuple(x) for x in weekday_medians_no_hour.reset_index()[['start_station_id', 'end_station_id']].values]
trips_to_predict = [x for x in all_possible_trips if x not in wmnh_trips]

# third step of prediction: finding midpoints between stations and adding medians for the component trips
mid_pred  = []
for (start, end) in trips_to_predict:
    mid_pred.append((start, end, predict_using_midpoint(start, end)))
midpoint_predicted_medians = pd.DataFrame(mid_pred, columns = ('start_station_id', 'end_station_id', 'tripduration'))
midpoint_predicted_medians = midpoint_predicted_medians.set_index(['start_station_id', 'end_station_id'])
midpoint_predicted_medians.save(midpoint_predicted_medians_file)