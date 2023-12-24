from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from threading import Thread
from io import BytesIO
import base64
import json
app = Flask('application', template_folder="/home/nemir/psy_slider/templates")

class Database:
    def __init__(self):
        self.users = {}
        self.choices = {}

    def add_user(self, user_id, role):
        self.users[user_id] = {'role': role, 'choices': []}

    def add_choice(self, user_id, choice):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.choices.setdefault(user_id, []).append({'timestamp': timestamp, 'choice': choice})
        self.users[user_id]['choices'].append({'timestamp': timestamp, 'choice': choice})

    def get_all_users(self):
        return self.users

    def get_user_choices(self, user_id):
        return self.choices.get(user_id, [])

db = Database()

# Route for serving the main page where users can choose their role
@app.route('/')
def serve_main_page():
    return render_template('main_page.html')

# Route for handling role selection
@app.route('/select_role', methods=['POST'])
def serve_select_role():
    user_id = request.form.get('user_id')
    role = request.form.get('role')

    db.add_user(user_id, role)

    if role == 'user':
        return redirect(url_for('serve_user_page', user_id=user_id))
    elif role == 'admin':
        return redirect(url_for('serve_admin_dashboard'))

# Route for serving the user page with a slider and send button
@app.route('/user_page/<user_id>', methods=['GET', 'POST'])
def serve_user_page(user_id):
    if request.method == 'POST':
        choice = request.form.get('choice')
        db.add_choice(user_id, choice)
    return render_template('user_page.html', user_id=user_id)

# Route for serving the admin dashboard
@app.route('/admin_dashboard')
def serve_admin_dashboard():
    all_users = db.get_all_users()
    return render_template('admin_dashboard.html', all_users=all_users)

@app.route('/user_history/<user_id>')
def serve_user_history(user_id):
    user_choices = db.get_user_choices(user_id)
    return render_template('user_history.html', user_id=user_id, user_choices=user_choices)