import smtplib
import atexit
import os

from email.message import EmailMessage
from apscheduler.schedulers.background import BackgroundScheduler

from app.routes import five_day_forecast

ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
ADMIN_EMAIL_PASSWORD = os.environ.get('ADMIN_EMAIL_PASSWORD')

email_list = ['yakbakzak@gmail.com', 'mathmania3@gmail.com']

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
scheduler.add_job(func=send_email, trigger='cron', hour=12)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())
