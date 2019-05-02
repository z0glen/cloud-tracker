from flask import Flask, render_template, jsonify, request
import requests
import time
import datetime
import json
import os
import threading
import pytz

from email.message import EmailMessage
from apscheduler.schedulers.background import BackgroundScheduler

from app import app

DARK_SKY_KEY = os.environ.get('DARK_SKY_KEY')

def set_interval(func, sec):
    def wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, wrapper)
    t.start()
    return t

def ping():
    r = requests.get('https://yuge-cloud-tracker.herokuapp.com/')

set_interval(ping, 1800)

def daily_forecast(t):
        r = requests.get('https://api.darksky.net/forecast/' + DARK_SKY_KEY + '/42.3601,-71.0589,' + str(t) + '?exclude=currently,flags')
        sunrise = r.json()['daily']['data'][0]['sunriseTime']
        sunset = r.json()['daily']['data'][0]['sunsetTime']
        for i, hour in enumerate(r.json()['hourly']['data']):
            if abs(hour['time'] - sunrise) <= 1800:
                sunrise_data = hour['summary']
                sunrise_cloud_cover = str(hour['cloudCover']*100)+'%'
            elif abs(hour['time'] - sunset) <= 1800:
                sunset_data = hour['summary']
                sunset_cloud_cover = str(hour['cloudCover']*100)+'%'
        data = {
            "sunrise": sunrise,
            "sunrise_data": sunrise_data,
            "sunrise_cloud_cover": sunrise_cloud_cover,
            "sunset": sunset,
            "sunset_data": sunset_data,
            "sunset_cloud_cover": sunset_cloud_cover
        }
        return data

def five_day_forecast():
    data = {}
    string = ""
    from_tz = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
    to_tz = pytz.timezone('US/Eastern')
    for i in range(5):
        t = int(time.time() + i*24*60*60)
        d = datetime.datetime.fromtimestamp(t).strftime('%A %m-%d-%Y')
        data[d] = daily_forecast(t)
        sunrise_string = datetime.datetime.fromtimestamp(data[d]['sunrise']).replace(tzinfo=from_tz).astimezone(to_tz).strftime('%H:%M')
        sunset_string = datetime.datetime.fromtimestamp(data[d]['sunset']).replace(tzinfo=from_tz).astimezone(to_tz).strftime('%H:%M')
        string += "On " + d + ", sunrise will be " + data[d]['sunrise_data'] + " (cloud cover: " + data[d]['sunrise_cloud_cover'] + ") at " + sunrise_string + " and sunset will be " + data[d]["sunset_data"] + " (cloud cover: " + data[d]['sunset_cloud_cover'] + ") at " + sunset_string + "\n"
    return string

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/data")
def data():
    t = int(time.time())
    print(t)
    print(DARK_SKY_KEY)
    r = requests.get('https://api.darksky.net/forecast/' + DARK_SKY_KEY + '/42.3601,-71.0589,' + str(t) + '?exclude=currently,flags')
    return jsonify(r.json())

@app.route("/form")
def form():
    d = request.args.get('date')
    t = int(datetime.datetime.strptime(d+"+0000", "%Y-%m-%d%z").timestamp() + 3600*12)
    print(t)
    lat = request.args.get('lat')
    long = request.args.get('long')
    r = requests.get('https://api.darksky.net/forecast/' + DARK_SKY_KEY + '/' + lat + ',' + long + ',' + str(t) + '?exclude=currently,flags')
    return jsonify(r.json())

if __name__ == '__main__':
    app.run(debug=True)
