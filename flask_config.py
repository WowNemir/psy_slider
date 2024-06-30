
import pathlib


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:test.db:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Development:
    cwd = pathlib.Path.cwd()
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(cwd / "instance" / "site.db")
    DEBUG = True


class Production:
    cwd = pathlib.Path.cwd() / "psy_slider"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(cwd / "instance" / "site.db")
