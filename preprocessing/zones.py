import pandas as pd
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
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

# merge bikeweather with manhattanstations to get start and end zones
# this also should have the effect of eliminating any trips with non-Manhattan endpoints
bikeweather = bikeweather.merge(manhattanstations[['id','zone']], left_on = "start_station_id", right_on = "id")
bikeweather = bikeweather.rename(columns = {'zone':'start_zone'})
bikeweather = bikeweather.drop('id', 1)
bikeweather = bikeweather.merge(manhattanstations[['id','zone']], left_on = "end_station_id", right_on = "id")
bikeweather = bikeweather.rename(columns = {'zone':'end_zone'})

hourzones = bikeweather.groupby(['start_zone', 'end_zone', 'hour'])
zonemph = hourzones.mean()['man_dist']/hourzones.mean()['tripduration'] * 3600
zonecount = hourzones.count()['man_dist']


for i in range(1,7):

    fig = plt.figure(figsize = (10, 5))
    plt.subplot(1,2,1)
    for j in range(1,7):
        thisplot = zonemph[i,j].plot(label="%d" % j, linewidth=2)
    plt.axis([0,23,0,12])
    thisplot.set_xlabel("hour of day")
    thisplot.set_ylabel("speed (mph)")
    thisplot.set_title("speed from zone %d to other zones" % i)
    thisplot.set_xticks([8, 12, 17, 22])
    thisplot.set_xticklabels(['8am', '12pm', '5pm', '10pm'])
    thisplot.set_axis_bgcolor('lightgray')
    plt.legend(loc='lower left')
    plt.subplot(1,2,2)
    for j in range(1,7):
        thatplot = zonecount[i,j].plot(label="%d" % j, linewidth=2)
    plt.axis([0,23,0,70000])
    thatplot.set_xlabel("hour of day")
    thatplot.set_ylabel("number of trips")
    thatplot.set_title("rides from zone %d to other zones" % i)
    thatplot.set_xticks([8, 12, 17, 22])
    thatplot.set_xticklabels(['8am', '12pm', '5pm', '10pm'])
    thatplot.set_axis_bgcolor('lightgray')
    plt.legend(loc='upper left')    
    savepath = "%szoneplot%d.png" % (path_for_img, i)
    plt.savefig(savepath)
