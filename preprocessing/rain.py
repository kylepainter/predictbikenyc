import pandas as pd
import numpy as np
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.simplefilter("ignore", category = FutureWarning) # eliminates pandas future warning for pickled df
warnings.simplefilter("ignore", category = UserWarning) # eliminates warning for colors being deprecated

project_location = '/home/vagrant/projectcode/predictbikenyc'
# bikeweather.file is 1.2GB and not needed for deployed website
# so it is not accessible via github. It can, however, be produced
# by the bikeweathercompilation.py script.
path_for_bikeweather = '/home/vagrant/projectcode/bikeweather.file'

bikeweather = pd.load(path_for_bikeweather)
path_for_img = project_location + '/app/static/img/'
sunrainspeed_image = path_for_img + 'sunrainspeed.png'
sunrainage_image = path_for_img + 'sunrainage.png'
sunraingender_image = path_for_img + 'sunraingender.png'
expectedrainspeed_image = path_for_img + 'expectedrainspeed.png'

bikesun = bikeweather[bikeweather.HourlyPrecip == 0]
bikerain = bikeweather[bikeweather.HourlyPrecip > 0]
bikerain = bikerain[bikerain.age > 0] # getting rid of riders under age 0, which are riders who didn't list an age
bikesun = bikesun[bikesun.age > 0]

# Plot comparing means of sunny vs. rainy days
sunmean = np.mean(bikesun.man_dist)/ np.mean(bikesun.tripduration) * 3600
rainmean = np.mean(bikerain.man_dist)/ np.mean(bikerain.tripduration) * 3600
allmean = np.mean(bikeweather.man_dist)/ np.mean(bikeweather.tripduration) * 3600 # 6.4211506442082289

sunrainspeed = pd.DataFrame({'weather':['rain', 'sun'], 'speed':[rainmean,sunmean]})
sunrainspeed = sunrainspeed.set_index('weather')
srsplot = sunrainspeed.plot(kind = 'bar', colors = 'by')
plt.axis([-1, 2, 5,7])
srsplot.set_ylabel("speed (mph)")
plt.xticks(rotation=0)
srsplot.legend().set_visible(False)
srsplot.set_axis_bgcolor('lightgray')
savepath = sunrainspeed_image 
plt.savefig(savepath)
plt.show()

#################

# Plot comparing age of sunny vs. rainy days
sunage = np.mean(bikesun.age)
rainage = np.mean(bikerain.age)
sunrainage = pd.DataFrame({'weather':['rain', 'sun'], 'age':[rainage,sunage]})
sunrainage = sunrainage.set_index('weather')
sraplot = sunrainage.plot(kind = 'bar', colors = 'by')
plt.axis([-1, 2, 34,40])
plt.xticks(rotation=0)
sraplot.set_ylabel("age")
sraplot.legend().set_visible(False)
sraplot.set_axis_bgcolor('lightgray')
savepath = sunrainage_image
plt.savefig(savepath)
plt.show()

# Plot comparing gender ratio of sunny vs. rainy days
sungender = len(bikesun[bikesun.gender == 1]) * 1.0 / len(bikesun[bikesun.gender == 2])
raingender = len(bikerain[bikerain.gender == 1]) * 1.0 / len(bikerain[bikerain.gender == 2])
sunraingender = pd.DataFrame({'weather':['rain', 'sun'], 'gender':[raingender,sungender]})
sunraingender = sunraingender.set_index('weather')
srgplot = sunraingender.plot(kind = 'bar', colors = 'by')
plt.axis([-1, 2, 0, 5])
srgplot.set_ylabel("ratio of men/women")
srgplot.legend().set_visible(False)
plt.xticks(rotation=0)
srgplot.set_axis_bgcolor('lightgray')
savepath = sunraingender_image
plt.savefig(savepath)
plt.show()

##################

# Plot comparing actual rainy day speed with expected speed 
# for the same demographic distribution were it a sunny day

bw_no_under_0 = bikeweather[bikeweather.age > 0] # getting rid of riders under age 0, which are riders who didn't list an age
agegender = bw_no_under_0.groupby(['age', 'gender'])
agegenderrain = bw_no_under_0[bw_no_under_0.HourlyPrecip > 0].groupby(['age', 'gender'])
agegendersun = bw_no_under_0[bw_no_under_0.HourlyPrecip == 0].groupby(['age', 'gender'])

agegenderraintotal = len(bikeweather[(bikeweather.HourlyPrecip > 0) & (bikeweather.age > 0)])
agegendersuntotal = len(bikeweather[(bikeweather.HourlyPrecip == 0) & (bikeweather.age > 0)])

agegendertotal = len(bikeweather[bikeweather.age > 0])
speedagegender = agegender.mean()['man_dist'] / agegender.mean()['tripduration'] * 3600

# average speed for age/gender during sunny weather
speedagegendersun = agegendersun.mean()['man_dist'] / agegendersun.mean()['tripduration'] * 3600 

# age/gender distribution of rainy day riders
raindist = agegenderrain.count()['man_dist'] / agegenderraintotal 

rainmean = np.mean(bikerain.man_dist)/ np.mean(bikerain.tripduration) * 3600

# expected mean speed = expected value of age/gender distribution times average speed for age/gender cohorts
expectedrainmean = sum((speedagegendersun * raindist)[(speedagegendersun * raindist).notnull()])

expectedrainspeed = pd.DataFrame({'weather':['actual', 'expected'], 'speed':[rainmean,expectedrainmean]})
expectedrainspeed = expectedrainspeed.set_index('weather')
exprplot = expectedrainspeed.plot(kind = 'bar', colors = 'bc')
plt.axis([-1, 2, 5,7.5])
exprplot.set_ylabel("speed (mph)")
plt.xticks(rotation=0)
exprplot.legend().set_visible(False)
exprplot.set_axis_bgcolor('lightgray')
savepath = expectedrainspeed_image
plt.savefig(savepath)
plt.show()