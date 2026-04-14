import pytest
from flask import Flask
from app import db, login_manager
# from app.admin import admin_bp
from app.auth import auth_bp
from app.booking import booking_bp
from app.courts import courts_bp


def create_app():
    app = Flask(__name__)
    app.config.update({
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "PAGE_SIZE": 2,
        "TESTING": True,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": '34y394yjsbdkjsdjksdh'
    })

    db.init_app(app)
    login_manager.init_app(app)

    # app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(courts_bp)

    login_manager.init_app(app)

    return app


@pytest.fixture(scope='session')
def test_app():
    app = create_app()
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def test_client(test_app):
    return test_app.test_client()


@pytest.fixture
def test_session(test_app):
    with test_app.app_context():
        yield db.session
        db.session.rollback()
        db.session.remove()


@pytest.fixture
def mock_cloudinary(monkeypatch):
    def fake_upload(file, **kwargs):
        return {'secure_url': 'https://fake-avatar.png'}

    monkeypatch.setattr('cloudinary.uploader.upload', fake_upload)