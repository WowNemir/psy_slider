import uuid
from flask import Blueprint, Flask, render_template, request, redirect, url_for
import bcrypt
from flask import jsonify
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
import os
from sqlalchemy.orm import joinedload
from flask_config import Development, Production
from db import db, User, Client, Session, SessionStatus, Choice, Question
from flask_cors import CORS

def create_app(config):
    app = Flask(__name__, static_folder='../frontend/build', static_url_path='', template_folder='templates')
    app.secret_key = os.getenv("FLASK_SECRET_KEY", default="default_secret_key_here")
    app.config.from_object(config)
    login_manager = LoginManager(app)
    login_manager.login_view = "/api/v1/login"
    db.init_app(app)

    CORS(app)
    swagger_blu = Blueprint('site', __name__, static_url_path='/static/', static_folder='static')
    app.register_blueprint(swagger_blu)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)


    def calculate_hash(password, salt):
        return bcrypt.hashpw(password.encode("utf-8"), salt.encode("utf-8")).decode("utf-8")


    def generate_salt():
        return bcrypt.gensalt().decode("utf-8")


    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    @app.route("/api/v1/auth/register", methods=["POST",])
    def register():
        username = request.form["username"]
        password = request.form["password"]
        
        def is_password_valid(password):
            return True
        
        existing_user = User.query.filter_by(username=username).first()
        
        if existing_user:
            return jsonify(message="Username already exists. Please choose a different one."), 400
        
        if not is_password_valid(password):
            return jsonify(message="Password is not valid"), 400
        
        salt = generate_salt()
        hashed_password = calculate_hash(password, salt)

        new_user = User(
            id=uuid.uuid1().hex, username=username, password=hashed_password, salt=salt
        )
        db.session.add(new_user)
        db.session.commit()

        return jsonify(success=True)

    @app.route("/api/v1/auth/login", methods=["POST"])
    def login():
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user:
            if bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):

                login_user(user)
                return jsonify(success=True)

        return jsonify(message="Invalid username or password"), 400        

    @app.route("/api/v1/client", methods=["POST"])
    @login_required
    def add_client():
        name = request.form.get("name")
        new_client = Client(id=uuid.uuid1().hex, name=name, user_id=current_user.id)
        db.session.add(new_client)
        db.session.commit()
        return jsonify(success=True)


    @app.route("/client_page/<share_uid>", methods=["POST", "GET"])
    def serve_client_page(share_uid):
        questions_type = request.args.get("type")

        session = Session.query.filter_by(share_uid=share_uid).first()
        client = session.client if session else None
        user = client.user if client else None

        if request.method == "POST":

            for question_id, value in request.form.items():
                new_choice = Choice(
                    choice=value,
                    client_id=client.id,
                    user_id=user.id,
                    question_id=question_id,
                    session_id=session.id,
                )
                db.session.add(new_choice)
            if questions_type == "pre":
                session.pre_session_completed = True
            elif questions_type == "post":
                session.post_session_completed = True

            if (
                session.pre_session_completed is True
                and session.post_session_completed is True
            ):
                session.status = SessionStatus.FINISHED
            db.session.commit()

        elif request.method == "GET":
            if questions_type == "pre" and not session.pre_session_completed:
                return render_template(
                    "client_page.html",
                    client=client,
                    session=session,
                    user_id=current_user.id,
                    questions_type=questions_type,
                    questions=Question().pre_session_questions,
                )
            elif questions_type == "post" and not session.post_session_completed:
                return render_template(
                    "client_page.html",
                    client=client,
                    session=session,
                    user_id=current_user.id,
                    questions_type=questions_type,
                    questions=Question().post_session_questions,
                )
        return render_template("thank_you_page.html")


    @app.route("/api/start_session/<client_id>", methods=["POST"])
    @login_required
    def start_session(client_id):
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


    @app.route("/api/finish_session/<client_id>", methods=["POST"])
    @login_required
    def finish_session(client_id):
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


    def set_has_unfinished_choices(client_id):
        client = Client.query.get(client_id)
        if client:
            client.has_unfinished_choices = True
            db.session.commit()


    @app.route("/api/set_has_unfinished_choices/<client_id>", methods=["POST"])
    @login_required
    def api_set_has_unfinished_choices(client_id):
        set_has_unfinished_choices(client_id)
        return jsonify({"status": "success"})


    @app.route("/api/choices/<client_id>")
    @login_required
    def get_client_choices(client_id):
        choices1 = (
            Choice.query.filter(
                Choice.client_id == client_id, Choice.question.has(type="before_session")
            )
            .options(joinedload(Choice.question))  # Eagerly load the related Question
            .order_by(Choice.timestamp)
            .all()
        )

        choices1_data = [
            {
                "timestamp": choice.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "choice": choice.choice,
                "question": choice.question.text,
                "theme": choice.question.theme,
            }
            for choice in choices1
        ]
        choices2 = (
            Choice.query.filter(
                Choice.client_id == client_id, Choice.question.has(type="before_session")
            )
            .options(joinedload(Choice.question))  # Eagerly load the related Question
            .order_by(Choice.timestamp)
            .all()
        )

        choices2_data = [
            {
                "timestamp": choice.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "choice": choice.choice,
                "question": choice.question.text,
                "theme": choice.question.theme,
            }
            for choice in choices2
        ]

        return jsonify([choices1_data, choices2_data])


    @app.route("/admin_dashboard/")
    @login_required
    def serve_admin_dashboard():
        clients = Client.query.filter_by(user_id=current_user.get_id()).all()
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
            psycho_id=current_user.get_id(),
        )


    @app.route("/client_history/<client_id>")
    @login_required
    def serve_client_history(client_id):
        client = Client.query.get(client_id)
        choices = Choice.query.filter_by(client_id=client_id).order_by("timestamp").all()
        return render_template("client_history.html", client=client, choices=choices)


    @app.route("/api/v1/auth/logout", methods=["POST"])
    @login_required
    def logout():
        logout_user()
        return jsonify(success=True)
    
    @app.route('/api/docs')
    def get_docs():
        print('sending docs')
        return render_template('swaggerui.html')
    
    return app



if __name__ == "__main__":
    configs = {
    'development': Development,
    'produuction': Production,
    }
    if not os.getenv("Environment"):
        from dotenv import load_dotenv
        load_dotenv()

    app = create_app(configs.get(os.getenv("Environment"), Development))
    app.run()
