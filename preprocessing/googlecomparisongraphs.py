import pandas as pd
import json
import requests
import warnings
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
warnings.simplefilter("ignore", category = FutureWarning) # eliminates pandas future warning for pickled df

project_location = '/home/vagrant/projectcode/predictbikenyc'
# bikeweather.file is 1.2GB and not needed for deployed website
# so it is not accessible via github. It can, however, be produced
# by the bikeweathercompilation.py script.
path_for_bikeweather = '/home/vagrant/projectcode/bikeweather.file'

path_for_img = project_location + '/app/static/img/'
path_for_df = project_location + '/app/static/dataframes/'
manhattanstations = pd.load(path_for_df + 'manhattanstations.file')
bikeweather = pd.load(path_for_bikeweather)
dates = pd.DatetimeIndex(bikeweather.starttime)
bikeweekday = bikeweather[dates.weekday < 5]

def main():

    thistriplist = [('432to293','google_close_to_median.png'), ('472to528','google_above_median.png'), \
                ('490to477','google_below_median.png'), ('514to426','fluctuating_by_hour.png')]

    # 432to293 = Google tracking closely with median / mean
    # 472to528 = Google (percentage wise), well above the mean/ median, and indeed, most riders
    # 490to477 = Google well below mean, and below almost all riders
    # 514to426 = fluctuating throughout day

    counter = 0
    #for tr in trip_index:
    filedirectory = '/home/vagrant/projectcode/predictbikenyc/app/static/img/'
    for (tr, filename) in thistriplist:
        create_graph(tr, filename)

def create_graph(tr, filename):
    fig = plt.figure(figsize=(10,8))
    start, stop = tr.split('to')
    gdur, gdist, gjson = get_google_time(start, stop)
    gdisttext = gjson['rows'][0]['elements'][0]['distance']['text']
    startname = manhattanstations.stationName[manhattanstations.id == start].values[0]
    stopname = manhattanstations.stationName[manhattanstations.id == stop].values[0]
    
    #heading
#    print("trip id %s, %s to %s" % (tr, startname, stopname) )
#    print("calculated distance = %f miles ; goodle distance = %s" % (bikeweather[bikeweather.trip == tr].iloc[1]['man_dist'], gdisttext))
    
    onetripwkdy = bikeweekday[(bikeweekday.trip == tr) & (bikeweekday.tripduration < 1800) & (bikeweekday.usertype == 'Subscriber') & (bikeweekday.HourlyPrecip == 0) ]
    onetripwkdy.plot(x = 'hour', y = 'tripduration', style = 'ro', label="Trips")
    a = onetripwkdy.groupby('hour').mean()['tripduration']
    thisplot = a.plot(style = 'b-', linewidth=2, label="Mean, N = %s" % len(onetripwkdy)) 
    b = onetripwkdy.groupby('hour').median()['tripduration']  
    b.plot(style= 'y-',linewidth=2, label="Median")
    

    plt.plot((0, 24), (gdur, gdur), 'c-', linewidth=2, label="Google Prediction")
    
    plt.axis([0, 24, 0, 1800])
    thisplot.set_xlabel("hour of day")
    thisplot.set_ylabel("trip duration (seconds)")
    thisplot.set_title("Weekday trips,   %s   to   %s" % (startname,stopname))
    thisplot.set_xticks([8, 12, 17, 22])
    thisplot.set_xticklabels(['8am', '12pm', '5pm', '10pm'])
    thisplot.set_axis_bgcolor('lightgray')
    plt.legend(loc='upper left')
    savepath = path_for_img + filename
    plt.savefig(savepath)
    plt.clf()


def get_google_time(start, stop):
    base = "https://maps.googleapis.com/maps/api/distancematrix/json"
    start_lat = str(manhattanstations.latitude[manhattanstations.id == start].values[0])
    start_long = str(manhattanstations.longitude[manhattanstations.id == start].values[0])
    end_lat = str(manhattanstations.latitude[manhattanstations.id == stop].values[0])
    end_long = str(manhattanstations.longitude[manhattanstations.id == stop].values[0])
    params =  { 'origins' : "%s,%s" % (start_lat, start_long),
                'destinations' : "%s,%s" % (end_lat, end_long),
                'units' : 'imperial',
                'mode' : "bicycling",
                'key' : "AIzaSyBG7MY4qQX4wj9VqKOje2uhE2nr0G2XPFU"
                }
    r = requests.get(base, params = params)
    j = json.loads(r.text)
    duration = j['rows'][0]['elements'][0]['duration']['value']
    distance = j['rows'][0]['elements'][0]['distance']['value']
    return duration, distance, j

main()
