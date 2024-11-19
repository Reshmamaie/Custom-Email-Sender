import os
import csv
import time
import pandas as pd
from flask import Flask, request, render_template, redirect, url_for, flash, session
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
USER_CSV_FILE = 'users.csv'

scheduler = BackgroundScheduler()
scheduler.start()

if not os.path.exists(USER_CSV_FILE):
    with open(USER_CSV_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['username', 'password'])  # Header row

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('send_custom_emails'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with open(USER_CSV_FILE, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username:
                    flash('Username already exists. Please choose a different username or log in.')
                    return redirect(url_for('register'))

        with open(USER_CSV_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([username, password])

        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with open(USER_CSV_FILE, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username and row['password'] == password:
                    session['username'] = username
                    flash('Login successful!!   ')
                    return redirect(url_for('send_custom_emails'))

        flash('Invalid credentials. Please try again or register.')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/send_custom_emails', methods=['GET', 'POST'])
def send_custom_emails():
    if 'username' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))

    columns = []
    email_sent_status = None
    scheduled_status = None

    if request.method == 'POST':
        file = request.files.get('file')
        target_email = request.form.get('target_email')
        custom_message = request.form.get('custom_message')
        schedule_time = request.form.get('schedule_time')
        throttle_rate = int(request.form.get('throttle_rate', 10))

        if file and file.filename.endswith('.csv'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            data = pd.read_csv(filepath)
            columns = data.columns.tolist()

            if 'Email' not in data.columns:
                flash("Error: 'Email' column not found. Please ensure the CSV contains an 'Email' column.")
                return redirect(url_for('send_custom_emails'))

            if target_email in data['Email'].values:
                row = data[data['Email'] == target_email].iloc[0]
                personalized_message = custom_message.format(**row)

                if schedule_time:
                    schedule_datetime = datetime.strptime(schedule_time, "%Y-%m-%d %H:%M")
                    scheduler.add_job(func=send_email, trigger='date', run_date=schedule_datetime,
                                      args=[target_email, personalized_message])
                    scheduled_status = f"Email to {target_email} scheduled for {schedule_time}."
                else:
                    send_email(target_email, personalized_message)
                    email_sent_status = f"Email sent successfully to {target_email}."
            else:
                email_sent_status = "Email not found."

    return render_template('send_emails.html', columns=columns, email_sent_status=email_sent_status,
                           scheduled_status=scheduled_status)

def send_email(to_email, message):
    print(f"Sending email to {to_email} with message:\n{message}")

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)