from flask import Flask, render_template, jsonify, request, url_for, flash, redirect
from flask_login import login_user, logout_user, current_user, login_required
import time
import json

from app import app, db
from app.forms import LoginForm, RegistrationForm, SettingsForm
from app.models import User
from app.forecast import daily_forecast

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Welcome to Cloud Tracker!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm(obj=current_user)
    if form.validate_on_submit():
        current_user.daily_email = form.daily_email.data
        db.session.commit()
        flash('Your preferences have been updated')
        return redirect(url_for('index'))
    return render_template('settings.html', title='Settings', form=form)

@app.route("/data")
def data():
    out = {}
    for i in range(5):
        t = int(time.time() + i*24*60*60)
        d = datetime.datetime.fromtimestamp(t).strftime('%A %m-%d-%Y')
        out[d] = daily_forecast(t)
    return json.dumps([out])

@app.route("/emails")
def get_emails():
    emails = [u.email for u in User.query.filter_by(daily_email=True).all()]
    return jsonify(emails)

if __name__ == '__main__':
    app.run(debug=True)
