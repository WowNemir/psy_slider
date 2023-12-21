from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import matplotlib.pyplot as plt
from flask import render_template, Flask
from threading import Thread
from io import BytesIO
import base64
import json
app = Flask(__name__)
app = Flask(__name__, template_folder='./templates')

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

def generate_graph(choices, callback):
    def background_task():
        timestamps, values = zip(*((choice['timestamp'], choice['choice']) for choice in choices))

        graph_data = {'timestamps': list(timestamps), 'values': list(values)}

        # Use the callback to perform UI-related operations
        callback(graph_data)

    # Run the background task in a separate thread
    thread = Thread(target=background_task)
    thread.start()

@app.route('/user_history/<user_id>')
def serve_user_history(user_id):
    user_choices = db.get_user_choices(user_id)

    def update_ui(graph_data):
        # Update the UI with Chart.js logic
        return render_template('user_history.html', user_id=user_id, user_choices=user_choices, graph_data=json.dumps(graph_data))

    generate_graph(user_choices, update_ui)
    return "Generating graph..."

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
