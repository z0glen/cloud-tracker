import smtplib
import os

from email.mime.text import MIMEText
from apscheduler.schedulers.background import BlockingScheduler

from app.routes import five_day_forecast

ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
ADMIN_EMAIL_PASSWORD = os.environ.get('ADMIN_EMAIL_PASSWORD')

email_list = ['yakbakzak@gmail.com', 'mathmania3@gmail.com']

scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron', hour=12)
def send_email():
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(ADMIN_EMAIL, ADMIN_EMAIL_PASSWORD)
    for to_address in email_list:
        msg = MIMEText(five_day_forecast(), "html")
        msg['Subject'] = '[Cloud Tracker] Five Day Forecast'
        msg['From'] = ADMIN_EMAIL
        msg['To'] = to_address
        s.send_message(msg)
    s.quit()

scheduler.start()
