from flask import Flask, render_template, jsonify, request
import requests
import time
import datetime
import smtplib
import atexit
import json
import os

from email.message import EmailMessage
from apscheduler.schedulers.background import BackgroundScheduler

from app import app

DARK_SKY_KEY = os.environ.get('DARK_SKY_KEY')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
ADMIN_EMAIL_PASSWORD = os.environ.get('ADMIN_EMAIL_PASSWORD')

email_list = ['yakbakzak@gmail.com', 'mathmania3@gmail.com']

def daily_forecast(t):
        r = requests.get('https://api.darksky.net/forecast/' + DARK_SKY_KEY + '/42.3601,-71.0589,' + str(t) + '?exclude=currently,flags')
        sunrise = r.json()['daily']['data'][0]['sunriseTime']
        sunset = r.json()['daily']['data'][0]['sunsetTime']
        for i, hour in enumerate(r.json()['hourly']['data']):
            if abs(hour['time'] - sunrise) <= 1800:
                sunrise_data = hour['summary']
            elif abs(hour['time'] - sunset) <= 1800:
                sunset_data = hour['summary']
        data = {
            "sunrise": sunrise,
            "sunrise_data": sunrise_data,
            "sunset": sunset,
            "sunset_data": sunset_data
        }
        return data

def five_day_forecast():
    data = {}
    string = ""
    for i in range(1, 6):
        t = int(time.time() + i*24*60*60)
        d = datetime.datetime.fromtimestamp(t).strftime('%m-%d-%Y')
        data[d] = daily_forecast(t)
        sunrise_string = datetime.datetime.fromtimestamp(data[d]['sunrise']).strftime('%H:%M')
        sunset_string = datetime.datetime.fromtimestamp(data[d]['sunset']).strftime('%H:%M')
        string += "On " + d + ", sunrise will be " + data[d]['sunrise_data'] + " at " + sunrise_string + " and sunset will be " + data[d]["sunset_data"] + " at " + sunset_string + "\n"
    return string

def send_email():
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(ADMIN_EMAIL, ADMIN_EMAIL_PASSWORD)
    for to_address in email_list:
        msg = EmailMessage()
        msg.set_content(five_day_forecast())
        msg['Subject'] = '[Cloud Tracker] Five Day Forecast'
        msg['From'] = ADMIN_EMAIL
        msg['To'] = to_address
        s.send_message(msg)
    s.quit()

scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(func=send_email, trigger='interval', hours=24)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/data")
def data():
    t = int(time.time())
    r = requests.get('https://api.darksky.net/forecast/' + DARK_SKY_KEY + '/42.3601,-71.0589,' + str(t) + '?exclude=currently,flags')
    return jsonify(r.json())

@app.route("/form")
def form():
    d = request.args.get('date')
    t = int(datetime.datetime.strptime(d, "%Y-%m-%d").timestamp())
    lat = request.args.get('lat')
    long = request.args.get('long')
    r = requests.get('https://api.darksky.net/forecast/' + DARK_SKY_KEY + '/' + lat + ',' + long + ',' + str(t) + '?exclude=currently,flags')
    return jsonify(r.json())

if __name__ == '__main__':
    app.run(debug=True)
