import smtplib
import os
import requests

from email.mime.text import MIMEText
from apscheduler.schedulers.background import BlockingScheduler

from app.forecast import five_day_forecast

ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
ADMIN_EMAIL_PASSWORD = os.environ.get('ADMIN_EMAIL_PASSWORD')

# email_list = ['yakbakzak@gmail.com', 'mathmania3@gmail.com']

def get_email_list():
    r = requests.get("http://127.0.0.1:5000/emails")
    return r.json()

scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron', hour=7)
def send_email():
    email_list = get_email_list()
    # s = smtplib.SMTP('smtp.gmail.com', 587)
    # s.starttls()
    # s.login(ADMIN_EMAIL, ADMIN_EMAIL_PASSWORD)
    for to_address in email_list:
        print(to_address)
        msg = MIMEText(five_day_forecast(), "html")
        msg['Subject'] = '[Cloud Tracker] Five Day Forecast'
        msg['From'] = ADMIN_EMAIL
        msg['To'] = to_address
        # s.send_message(msg)
    # s.quit()

# scheduler.start()
send_email()
