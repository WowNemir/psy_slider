import pytest
from main import create_app
from db import db, User
from flask_config import TestConfig
import pytest


@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as testclient:
        with app.app_context():
            db.create_all()
            yield testclient
            db.session.remove()
            db.drop_all()

def test_main_page(client):
    response = client.get('/')
    assert response.status_code == 200

def test_user_registration(client):
    response = client.post('/register', data={
        'new_username': 'testuser',
        'new_password': 'password',
        'confirm_password': 'password'
    })
    assert response.status_code == 302
    user = User.query.filter_by(username='testuser').first()
    assert user is not None

def test_user_login(client):
    client.post('/register', data={
        'new_username': 'testuser',
        'new_password': 'password',
        'confirm_password': 'password'
    })
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    })
    assert response.status_code == 302  # Redirect to dashboard
