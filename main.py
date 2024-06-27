import uuid
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt
import pathlib
from flask import jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
import os

app = Flask(__name__, template_folder="templates", static_folder="static/css")
app.secret_key = os.getenv('FLASK_SECRET_KEY', default='default_secret_key_here')
login_manager = LoginManager(app)
login_manager.login_view = 'login'

cwd = pathlib.Path.cwd()

def is_production():
    return str(cwd).endswith('nemir')

if is_production():
    cwd = cwd / "psy_slider"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + str(cwd / 'instance' / 'site.db')
db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    id = db.Column(db.String(50), primary_key=True)
    role = db.Column(db.String(10))
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    salt = db.Column(db.String(255))
    clients = db.relationship('Client', backref='user', lazy=True)
    choices = db.relationship('Choice', backref='user', lazy=True)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(50), db.ForeignKey('client.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.now)
    pre_session_completed = db.Column(db.Boolean, default=False)
    post_session_completed = db.Column(db.Boolean, default=False)
    choices = db.relationship('Choice', backref='session', lazy=True)

class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    choice = db.Column(db.Integer)
    question = db.Column(db.String(255))
    share_link = db.Column(db.String(255))
    client_id = db.Column(db.String(50), db.ForeignKey('client.id'), nullable=False)
    user_id = db.Column(db.String(50), db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)


class Client(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(255))
    psycho_id = db.Column(db.String(50), db.ForeignKey('user.id'), nullable=False)
    has_unfinished_choices = db.Column(db.Boolean, default=False)
    choices = db.relationship('Choice', backref='client', lazy=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

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

    if user:
        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):

            login_user(user)
            return redirect(url_for('serve_admin_dashboard'))
    
    return "Invalid username or password"

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
@login_required
def add_client():
    if request.method == 'POST':
        name = request.form.get('name')
        new_client = Client(id=uuid.uuid1().hex, name=name, psycho_id=current_user.id)
        db.session.add(new_client)
        db.session.commit()
        return redirect(url_for('serve_admin_dashboard'))
    return render_template('add_client.html', psycho_id=current_user.get_id())


questions1 = {
    "Индивидуально": "Как вы оцениваете ваше индивидуальное благополучие на прошедшей неделе?",
    "В личных отношениях": "Как вы оцениваете ваши личные отношения за прошедшую неделю?",
    "Социально": "Как вы оцениваете ваше социальное состояние на прошедшей неделе?",
    "Личное благополучие": "Как вы оцениваете ваше общее ощущение благополучия на прошедшей неделе?"
}
questions2 = {
    'Отношение': "Чувствовали ли вы, что ваше отношение было положительно оценено и уважаемо?",
    'Цели и темы': "Были ли обсуждены те темы или задачи, которые вы считали важными для данной консультации?",
    'Подход и метод': "Насколько подход и метод работы терапевта соответствовали вашим ожиданиям и предпочтениям?",
    'В целом': "Каково ваше общее впечатление от сегодняшней консультации?"
}
@app.route('/client_page/<psycho_id>/<client_id>', methods=['GET', 'POST'])
def serve_client_page(client_id, psycho_id):
    client = Client.query.filter_by(id=client_id).first()

    if client.has_unfinished_choices and request.method == 'POST':
        choices = []
        for key, value in request.form.items():
            question = questions1.get(key) or questions2.get(key) or "unknown question"
            choices.append((value, question))
        
        for choice, question in choices:
            new_choice = Choice(choice=choice, client_id=client_id, user_id=psycho_id, question=question)
            db.session.add(new_choice)
        db.session.commit()
        
        client.has_unfinished_choices = False
        db.session.commit()

        return render_template('thank_you_page.html')
    elif client.has_unfinished_choices:
        return render_template('client_page.html', client=client, psycho_id=psycho_id, questions1=questions1, questions2=questions2)
    else:
        return render_template('thank_you_page.html')

def set_has_unfinished_choices(client_id):
    client = Client.query.get(client_id)
    if client:
        client.has_unfinished_choices = True
        db.session.commit()

@app.route('/api/set_has_unfinished_choices/<client_id>', methods=['POST'])
@login_required
def api_set_has_unfinished_choices(client_id):
    set_has_unfinished_choices(client_id)
    return jsonify({'status': 'success'})


@app.route('/api/choices/<client_id>')
@login_required
def get_client_choices(client_id):

    choices1 = Choice.query.filter(Choice.client_id == client_id, Choice.question.in_(questions1.values())).order_by(Choice.timestamp).all()
    choices1_data = [{'timestamp': choice.timestamp.strftime('%Y-%m-%d %H:%M:%S'), 'choice': choice.choice, 'question': choice.question} for choice in choices1]

    choices2 = Choice.query.filter(Choice.client_id == client_id, Choice.question.in_(questions2.values())).order_by(Choice.timestamp).all()
    choices2_data = [{'timestamp': choice.timestamp.strftime('%Y-%m-%d %H:%M:%S'), 'choice': choice.choice, 'question': choice.question} for choice in choices2]

    return jsonify([choices1_data, choices2_data])


@app.route('/admin_dashboard/')
@login_required
def serve_admin_dashboard():
  clients = Client.query.filter_by(psycho_id=current_user.get_id()).all()
  return render_template('admin_dashboard.html', clients=clients, psycho_id=current_user.get_id())


@app.route('/client_history/<client_id>')
@login_required
def serve_client_history(client_id):
    client = Client.query.get(client_id)
    choices = Choice.query.filter_by(client_id=client_id).order_by("timestamp").all()
    return render_template('client_history.html', client=client, choices=choices)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('serve_main_page'))


if __name__ == "__main__":
    if is_production:
        app.run()
    else:
        app.run(debug=True)
