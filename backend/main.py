import sys
import os
import uuid
from flask import Blueprint, Flask, render_template, request, redirect, send_from_directory, url_for, jsonify
import bcrypt
from sqlalchemy.orm import joinedload
from db import db, User, Client, Session, SessionStatus, Choice, Question, client_schema, choice_schema
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, current_user, jwt_required
from flask_config import Development, Production
from auth import safe_parse_webapp_init_data, check_integrity


def create_app(*args):
    config = Development
    app = Flask(__name__, static_folder='../frontend/build', static_url_path='', template_folder='templates')
    app.secret_key = os.getenv("FLASK_SECRET_KEY", default="default_secret_key_here")
    app.url_map.strict_slashes = False
    app.config.from_object(config)
    db.init_app(app)
    CORS(app)
    jwt = JWTManager(app)    
    def calculate_hash(password, salt):
        return bcrypt.hashpw(password.encode("utf-8"), salt.encode("utf-8")).decode("utf-8")

    def generate_salt():
        return bcrypt.gensalt().decode("utf-8")

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.id

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity).one_or_none()

    @app.route("/api/v1/auth/register", methods=["POST"])
    def register(username=None, password=None):
        username = username or request.form["new_username"]
        password = password or request.form["new_password"]

        def is_password_valid(password):
            return True

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            return jsonify(message="Username already exists. Please choose a different one."), 400

        if not is_password_valid(password):
            return jsonify(message="Password is not valid"), 400


        _register(username, password)
        
        return jsonify(success=True)
    
    def _register(username, password=None, telegram_id=None):
        import random
        password = password or str(random)
        salt = generate_salt()
        hashed_password = calculate_hash(password, salt)
        if telegram_id:
            new_user = User(
                id=uuid.uuid1().hex, username=username, password=hashed_password, salt=salt, telegram_id=telegram_id,
            )
        else:
            new_user = User(
                id=uuid.uuid1().hex, username=username, password=hashed_password, salt=salt
            )
        db.session.add(new_user)
        db.session.commit()
        return new_user
    
    
    @app.route("/api/v1/auth/login", methods=["POST"])
    def login():
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).one_or_none()
        if not user or not user.check_password(password):
            return jsonify("Wrong username or password"), 401

        access_token = create_access_token(identity=user)
        return jsonify(access_token=access_token)

    @app.route("/api/v1/clients", methods=["POST"])
    @jwt_required()
    def add_client():
        name = request.form.get("name")
        new_client = Client(id=uuid.uuid1().hex, name=name, user_id=current_user.id)
        db.session.add(new_client)
        db.session.commit()
        return jsonify(success=True)

    @app.route("/api/v1/clients", methods=["GET"])
    @jwt_required()
    def clients_info():
        clients = Client.query.filter_by(user_id=current_user.id, deleted=False).all()
        return jsonify(client_schema.dump(clients))
    
    @app.route("/api/v1/clients/<client_id>", methods=["GET"])
    @jwt_required()
    def client_info(client_id):
        client = Client.query.filter_by(id=client_id).one_or_404()
        return jsonify(client_schema.dump(client, many=False))

    @app.route("/api/v1/clients/<client_id>", methods=["DELETE"])
    @jwt_required()
    def client_delete(client_id):
        client = Client.query.filter_by(id=client_id).one_or_404()
        client.deleted = True
        db.session.commit()
        return jsonify(success=True)

    @app.route("/api/v1/clients/<client_id>/choices", methods=["GET"])
    @jwt_required()
    def get_choices(client_id):
        client = Client.query.filter_by(user_id=current_user.id, id=client_id, deleted=False).one_or_404()

        pre_session_questions_ids = [q.id for q in Question().pre_session_questions]
        post_session_questions_ids = [q.id for q in Question().post_session_questions]

        choices_pre = Choice.query.filter(Choice.client_id == client.id, Choice.question_id.in_(pre_session_questions_ids)).all()
        choices_post = Choice.query.filter(Choice.client_id == client.id, Choice.question_id.in_(post_session_questions_ids)).all()
        return jsonify(choice_schema.dump(choices_pre), choice_schema.dump(choices_post))

    @app.route("/api/v1/vote/<share_uid>", methods=["POST", "GET"])
    def get_choice_results(share_uid):
        session = Session.query.filter_by(share_uid=share_uid).one_or_404()
            
        client = session.client if session else None
        user = client.user if client else None
        type_ = request.args.get('type')
        if request.method == "GET":
            if type_ == 'pre' and session.pre_session_completed:
                return jsonify(True)
            elif type_ == 'post' and session.post_session_completed:
                return jsonify(True)
            return jsonify(False)
        for question_id, value in request.form.items():
            new_choice = Choice(
                    choice=value,
                    client_id=client.id,
                    user_id=user.id,
                    question_id=question_id,
                    session_id=session.id,
                )
            db.session.add(new_choice)
        if type_ == "pre":
            session.pre_session_completed = True
        elif type_ == "post":
            session.post_session_completed = True
        db.session.commit()
        return jsonify(success=True)

    @app.route("/api/v1/clients/<client_id>/sessions", methods=["POST"])
    @jwt_required()
    def new_session(client_id):
        client = Client.query.get(client_id)
        if client:
            active_session = Session.query.filter_by(
                client_id=client_id, status=SessionStatus.STARTED
            ).first()
            if active_session:
                return jsonify(
                    {
                        "status": "success",
                        "message": "Session already started",
                        "session_id": active_session.id,
                    }
                )
            new_session = Session(client_id=client_id, status=SessionStatus.STARTED)
            db.session.add(new_session)
            db.session.commit()
            return jsonify({"status": "success", "session_id": new_session.id})
        return jsonify({"status": "error", "message": "Client not found"}), 404

    @app.route("/api/v1/clients/<client_id>/sessions/<session_id>/finish", methods=["PATCH"])
    @jwt_required()
    def finish_session(client_id, session_id):
        session = Client.query.get(client_id).active_session

        if session:
            if session.status == SessionStatus.STARTED:
                session.finish()
                db.session.commit()
                return jsonify(
                    {
                        "status": "success",
                        "message": f"Session {session.id} finished successfully",
                    }
                )
            else:
                return jsonify(
                    {"status": "error", "message": f"Session {session.id} already finished"}
                )
        else:
            return jsonify({"status": "error", "message": "Session not found"}), 404

    @app.route("/admin_dashboard/")
    @jwt_required()
    def serve_admin_dashboard():
        clients = Client.query.filter_by(user_id=current_user.id).all()
        clients_with_sessions = []
        for client in clients:
            session = client.active_session
            clients_with_sessions.append(
                {
                    "client": client,
                    "active_session": session,
                }
            )

        return render_template(
            "admin_dashboard.html",
            clients=clients_with_sessions,
            psycho_id=current_user.id,
        )

    @app.route("/client_history/<client_id>")
    @jwt_required()
    def serve_client_history(client_id):
        client = Client.query.get(client_id)
        choices = Choice.query.filter_by(client_id=client_id).order_by("timestamp").all()
        return render_template("client_history.html", client=client, choices=choices)

    @app.route("/api/v1/auth/logout", methods=["POST"])
    @jwt_required()
    def logout():
        return jsonify(success=True)
    
    @app.route("/api/v1/questions/<questions_type>", methods=["GET"])
    def get_questions(questions_type):
        if questions_type == "pre":
            questions = Question().pre_session_questions
        elif questions_type == "post":
            questions = Question().post_session_questions
        else:
            return jsonify({"status": "error", "message": "Invalid question type"}), 400
        questions = [{"id": q.id, "text": q.text} for q in questions]
        return jsonify(questions)
    
    @app.route("/api/v1/auth/telegram", methods=["POST"])
    def auth_telegram():

        data = request.json['body']
        token=os.getenv('BOT_TOKEN')
        not_widget = False
        try:
            check_integrity(token, data)
            telegram_id = data['id']
        except Exception:
            not_widget = True
        if not_widget:
            try:
                data = safe_parse_webapp_init_data(token, init_data=data)
                telegram_id = data.user.id

            except ValueError:
                return jsonify({"ok": False, "err": "Unauthorized"}), 401
            
        user = User.query.filter(User.telegram_id == telegram_id).one_or_none()
        if user:
            access_token = create_access_token(identity=user)
        else:
            new_user = _register(username=data.user.username, telegram_id=telegram_id)
            access_token = create_access_token(identity=new_user)
        return jsonify(access_token=access_token)

    if config == Production:
        ...
    @app.route('/')
    def index(*args, **kwargs):
        return app.send_static_file('index.html')
    @app.errorhandler(404)   
    def not_found(e):   
        return app.send_static_file('index.html')
    return app
app = create_app()
# app.run(port=8000)
