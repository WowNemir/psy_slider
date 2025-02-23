from marshmallow import fields
import bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum
import uuid

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    role = db.Column(db.String(10))
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    salt = db.Column(db.String(255))
    telegram_id = db.Column(db.String(255), index=True, unique=True, nullable=True)

    clients = db.relationship("Client", backref="user", lazy=True)
    choices = db.relationship("Choice", backref="user", lazy=True)

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.password.encode("utf-8"))

class SessionStatus(enum.Enum):
    STARTED = "started"
    FINISHED = "finished"
    CANCELED = "canceled"

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.String(50), db.ForeignKey("client.id"), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.now)
    pre_session_completed = db.Column(db.Boolean, default=False)
    post_session_completed = db.Column(db.Boolean, default=False)
    status = db.Column(db.Enum(SessionStatus), default=SessionStatus.STARTED)
    share_uid = db.Column(db.String(50), default=lambda: uuid.uuid4().hex)
    choices = db.relationship("Choice", backref="session", lazy=True)
    client = db.relationship("Client", backref="sessions", lazy=True)

    def cancel(self):
        self.status = SessionStatus.CANCELED
        db.session.commit()

    def finish(self):
        self.status = SessionStatus.FINISHED
        db.session.commit()

    @property
    def active_choices(self):
        return Choice.query.filter_by(session_id=self.id).all()

class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    choice = db.Column(db.Integer)
    client_id = db.Column(db.String(50), db.ForeignKey("client.id"), nullable=False)
    user_id = db.Column(db.String(50), db.ForeignKey("user.id"), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey("session.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)

    @property
    def session_info(self):
        return Session.query.filter_by(id=self.session_id).first()

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    theme = db.Column(db.String(255), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    choices = db.relationship("Choice", backref="question", lazy=True)

    @property
    def pre_session_questions(self):
        return Question.query.filter_by(type="before_session").all()

    @property
    def post_session_questions(self):
        return Question.query.filter_by(type="after_session").all()

class Client(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(255))
    user_id = db.Column(db.String(50), db.ForeignKey("user.id"), nullable=False)
    deleted = db.Column(db.Boolean, default=False)
    choices = db.relationship("Choice", backref="client", lazy=True)

    @property
    def active_session(self):
        active_session = Session.query.filter_by(
            client_id=self.id, status=SessionStatus.STARTED
        ).first()
        return active_session if active_session else None

    @property
    def client_choices(self):
        return Choice.query.filter_by(client_id=self.id).all()

class SessionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Session
        load_instance = True

    id = fields.String()
    pre_session_completed = fields.Boolean()
    post_session_completed = fields.Boolean()
    status = fields.String()

class ClientSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Client
        load_instance = True

    id = fields.String()
    name = fields.String()
    active_session = fields.Nested(SessionSchema, many=False, dump_only=True)

class ChoiceSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Choice
        load_instance = True

    id = fields.Integer()
    timestamp = fields.DateTime()
    choice = fields.Integer()
    client_id = fields.String()
    user_id = fields.String()
    session_id = fields.Integer()
    question_id = fields.Integer()

client_schema = ClientSchema(many=True)
choice_schema = ChoiceSchema(many=True)
