import uuid
from flask import Flask, render_template, request, redirect, url_for
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

def create_app(config):
    app = Flask(__name__, template_folder="templates", static_folder="static/css")
    app.secret_key = os.getenv("FLASK_SECRET_KEY", default="default_secret_key_here")
    app.config.from_object(config)
    login_manager = LoginManager(app)
    login_manager.login_view = "login"
    db.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)


    def calculate_hash(password, salt):
        return bcrypt.hashpw(password.encode("utf-8"), salt.encode("utf-8")).decode("utf-8")


    def generate_salt():
        return bcrypt.gensalt().decode("utf-8")


    @app.route("/")
    def serve_main_page():
        return render_template("main_page.html")


    @app.route("/login", methods=["GET"])
    def serve_login_page():
        return render_template("login_page.html")


    @app.route("/register", methods=["GET", "POST"])
    def serve_register_page():
        if request.method == 'POST':
            new_username = request.form["new_username"]
            new_password = request.form["new_password"]
            confirm_password = request.form["confirm_password"]

            existing_user = User.query.filter_by(username=new_username).first()
            if existing_user:
                return "Username already exists. Please choose a different one."

            if new_password != confirm_password:
                return "Passwords do not match."

            salt = generate_salt()
            hashed_password = calculate_hash(new_password, salt)

            new_user = User(
                id=uuid.uuid1().hex, username=new_username, password=hashed_password, salt=salt
            )
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for("serve_main_page"))

        return render_template("register_page.html")


    @app.route("/login", methods=["POST"])
    def login():
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user:
            if bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):

                login_user(user)
                return redirect(url_for("serve_admin_dashboard"))

        return "Invalid username or password"
        

    @app.route("/add_client", methods=["GET", "POST"])
    @login_required
    def add_client():
        if request.method == "POST":
            name = request.form.get("name")
            new_client = Client(id=uuid.uuid1().hex, name=name, user_id=current_user.id)
            db.session.add(new_client)
            db.session.commit()
            return redirect(url_for("serve_admin_dashboard"))
        return render_template("add_client.html", user_id=current_user.get_id())


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


    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("serve_main_page"))
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
