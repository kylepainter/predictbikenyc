from flask import render_template, flash, redirect, request, url_for
from app import app
from Forms import PredictForm
from math import ceil
from datetime import datetime
import pandas as pd
import urllib2, json

path_to_project = '/home/vagrant/projectcode/predictbikenyc/'
dataframe_dir = '/app/static/dataframes/'

with open('apikeys.txt') as infile:
    opencage_apikey = infile.readline().strip().split('=')[1]
    googleapikey = infile.readline().strip().split('=')[1]

stations = pd.load('.%smanhattanstations.file' % (dataframe_dir))
weekday_medians =  pd.load('.%sweekday_medians.file' % ( dataframe_dir))
weekday_medians_no_hour = pd.load('.%sweekday_medians_no_hour.file' % ( dataframe_dir))
midpoint_medians = pd.load('.%smidpoint_medians.file' % ( dataframe_dir))
hour_scaling = pd.load('.%shour-scaling.file' % ( dataframe_dir))
hours = ['Now','6:00am','7:00am','8:00am','9:00am','10:00am','11:00am','12:00pm','1:00pm','2:00pm','3:00pm','4:00pm','5:00pm', \
        '6:00pm','7:00pm','8:00pm','9:00pm','10:00pm','11:00pm','12:00am','1:00am','2:00am','3:00am','4:00am','5:00am']

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
                           title='Home'
                           )

@app.route('/zones', methods=['GET'])
def zones():
    return render_template('zones.html', title='Geographic zones', googleapikey = googleapikey)

@app.route('/rain', methods=['GET'])
def rain():
    return render_template('rain.html',title='Biking in the Rain') 


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    distance_tolerance = .3
    title = 'Get a Prediction'
    form = PredictForm()
    if request.args.has_key('startlatlong'):  
        querystring = request.args
        if querystring['startlatlong'] == '':
            flash('Please select coordinates.')
            return render_template('predict.html', title=title, form=form, data = None, outofbounds = False)
        slat, slng = querystring['startlatlong'].split(',')
        elat, elng = querystring['endlatlong'].split(',')
        latlongs = [querystring['startlatlong'],querystring['endlatlong']]
        if (find_distance_to_nearest_station(float(slat), float(slng)) > distance_tolerance) or \
                (find_distance_to_nearest_station(float(elat), float(elng)) > distance_tolerance):
            flash('At least one of those coordinates was out of bounds.')
            return render_template('predict.html', title=title, form=form, data = querystring, latlongs = latlongs, outofbounds = True, hours = hours, googleapikey = googleapikey)
        address1 = get_address_from_latlong(slat, slng)
        address2 = get_address_from_latlong(elat, elng)
        hourint, hourtext = converthour(querystring['hour'])
        seconds = predictfromlatlong(float(slat), float(slng), 
                                float(elat), float(elng), hourint)  
        minutes = "%.2f" % (seconds * 1.0 / 60)
        return render_template('predict.html', title=title, form=form, data = querystring, triptime = minutes, latlongs = latlongs, \
                                hourtext = hourtext, outofbounds = False, address1 = address1, address2 = address2, hours = hours, googleapikey = googleapikey)
    else:
        return render_template('predict.html', title=title, form=form, data = None, outofbounds = False, hours = hours, googleapikey = googleapikey)

def converthour(hourstr):
    hourtext = hourstr
    if hourstr == "Now":
        hourint = datetime.now().hour
        if hourint > 12:
            hourtext = str(hourint - 12) + ":00 pm"
        elif hourint == '0':
            hourtext = "12:00 am"
        else:
            hourtext = str(hourint) + ":00 am"
    else:
        h = hourstr.split(":00")
        hourint = int(h[0])
        if 'pm' in h[1] and hourint != 12:
            hourint += 12
        if hourint == 12 and 'am' in h[1]:
            hourint = 0
    return hourint, hourtext

def predictfromlatlong(slat, slng, elat, elng, hour):
    s_ref_station = find_nearest_station(slat, slng)
    e_ref_station = find_nearest_station(elat, elng) 
    if s_ref_station == e_ref_station: 
        # if reference stations are the same (i.e., it's a very short trip)
        # man_dist in miles / (mean speed of hours * convert_to_seconds * hour_scaling)
        return (abs(slat - elat) * 69 + abs(slng - elng) * 52.5) * 3600 / (6.685 * hour_scaling[hour])
    s_ref_lat, s_ref_lng = stations.ix[s_ref_station].latitude, stations.ix[s_ref_station].longitude
    e_ref_lat, e_ref_lng = stations.ix[e_ref_station].latitude, stations.ix[e_ref_station].longitude
    startid, endid = stations.ix[s_ref_station].id.astype(str), stations.ix[e_ref_station].id.astype(str)
    ratio = man_dist_ratio(slat, slng, elat, elng, s_ref_lat, s_ref_lng, e_ref_lat, e_ref_lng)

    try:
        ref_tripduration = weekday_medians[hour][startid][endid]

    except:
        try:
            ref_tripduration = weekday_medians_no_hour[startid][endid]* hour_scaling[hour]
        except:
            print startid, endid
            ref_tripduration = midpoint_medians.xs(startid).xs(endid)* hour_scaling[hour]
    ref_tripduration *= ratio
    return int(ceil(ref_tripduration))

def man_dist_ratio(lat1s, lng1s, lat1e, lng1e, lat2s, lng2s, lat2e, lng2e):
    man_dist1 = abs(lat1s - lat1e) * 69 + abs( lng1s-lng1e ) * 52.5 
    man_dist2 = abs(lat2s - lat2e) * 69 + abs( lng2s-lng2e ) * 52.5
    print man_dist1 / man_dist2
    return man_dist1 / man_dist2

def find_nearest_station(lat, lng):
    difflat = abs(stations.latitude - lat)
    difflong = abs(stations.longitude - lng)
    man_diff = (abs(difflong) * 52.5) + (abs(difflat) * 69) 
    return man_diff.idxmin()

def find_distance_to_nearest_station(lat, lng):
    difflat = abs(stations.latitude - lat)
    difflong = abs(stations.longitude - lng)
    man_diff = (abs(difflong) * 52.5) + (abs(difflat) * 69) 
    return min(man_diff)

def get_address_from_latlong(lat, lng):
    lat = lat.strip()
    lng = lng.strip()

    url = "https://api.opencagedata.com/geocode/v1/json?q=%s+%s&key=%s" % (lat, lng, opencage_apikey)
    ret = urllib2.urlopen(url).read()
    addjson =  json.loads(ret)
    address = addjson['results'][0]['formatted'].split(', New York City NY')[0]
    return address

