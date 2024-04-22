import uuid
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt
import pathlib

app = Flask(__name__, template_folder="templates")

cwd = pathlib.Path.cwd()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + str(cwd / 'instance' / 'site.db')
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    role = db.Column(db.String(10))
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    salt = db.Column(db.String(255))
    clients = db.relationship('Client', backref='user', lazy=True)
    choices = db.relationship('Choice', backref='user', lazy=True)

class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    choice = db.Column(db.Integer)
    client_id = db.Column(db.String(50), db.ForeignKey('client.id'), nullable=False)
    user_id = db.Column(db.String(50), db.ForeignKey('user.id'), nullable=False)

class Client(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(255))
    psycho_id = db.Column(db.String(50), db.ForeignKey('user.id'), nullable=False)
    choices = db.relationship('Choice', backref='client', lazy=True)

def calculate_hash(password, salt):
    return bcrypt.hashpw(password.encode('utf-8'), salt.encode('utf-8')).decode('utf-8')

def generate_salt():
    return bcrypt.gensalt().decode('utf-8')

@app.route('/')
def serve_main_page():
    return render_template('main_page.html')

@app.route('/login', methods=['GET'])
def serve_login_page():
    return render_template('login_page.html')

@app.route('/register', methods=['GET'])
def serve_register_page():
    return render_template('register_page.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user and calculate_hash(password, user.salt) == user.password:
        return redirect(url_for('serve_admin_dashboard', psycho_id=user.id))
    else:
        return "Invalid username or password"

@app.route('/register', methods=['POST'])
def register():
    new_username = request.form['new_username']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    existing_user = User.query.filter_by(username=new_username).first()
    if existing_user:
        return "Username already exists. Please choose a different one."

    if new_password != confirm_password:
        return "Passwords do not match."

    salt = generate_salt()
    hashed_password = calculate_hash(new_password, salt)

    new_user = User(id=uuid.uuid1().hex, username=new_username, password=hashed_password, salt=salt)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('serve_main_page'))
@app.route('/add_client', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        name = request.form.get('name')
        # Assuming the currently logged-in user is the psycho
        psycho_id = request.form.get('user_id')
        new_client = Client(id=uuid.uuid1().hex, name=name, psycho_id=psycho_id)
        db.session.add(new_client)
        db.session.commit()
        return redirect(url_for('serve_admin_dashboard', psycho_id=psycho_id))
    return render_template('add_client.html')

# Route for serving the user page with a slider and send button
@app.route('/client_page/<psycho_id>/<client_id>', methods=['GET', 'POST'])
def serve_client_page(client_id, psycho_id):
    client = Client.query.filter_by(id=client_id).first()

    if request.method == 'POST':
        choice = request.form.get('choice')
        new_choice = Choice(choice=choice, client_id=client_id, user_id=psycho_id)
        db.session.add(new_choice)
        db.session.commit()
        return render_template('thank_you_page.html')
    return render_template('client_page.html', client=client, psycho_id=psycho_id)

@app.route('/admin_dashboard/<psycho_id>')
def serve_admin_dashboard(psycho_id):
  clients = Client.query.all()
  return render_template('admin_dashboard.html', clients=clients, psycho_id=psycho_id)

@app.route('/client_history/<client_id>')
def serve_client_history(client_id):
    client = Client.query.get(client_id)
    choices = Choice.query.filter_by(client_id=client_id).all()
    return render_template('client_history.html', client=client, choices=choices)

if __name__ == "__main__":
    app.run(debug=True)
