import pytest
from app import app as flask_app, db
from app.admin import admin_bp
from app.auth import auth_bp
from app.booking import booking_bp
from app.courts import courts_bp


@pytest.fixture
def test_app():
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if 'auth_bp' not in flask_app.blueprints:
        flask_app.register_blueprint(auth_bp)

    if 'courts_bp' not in flask_app.blueprints:
        flask_app.register_blueprint(courts_bp)

    if 'booking_bp' not in flask_app.blueprints:
        flask_app.register_blueprint(booking_bp)

    if 'admin_bp' not in flask_app.blueprints:
        flask_app.register_blueprint(admin_bp)

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def test_client(test_app):
    return test_app.test_client()


@pytest.fixture
def test_session(test_app):
    yield db.session
    db.session.rollback()

@pytest.fixture
def mock_cloudinary(monkeypatch):
    def fake_upload(file):
        return {'secure_url': 'https://fake-avatar.png'}

    monkeypatch.setattr('cloudinary.uploader.upload', fake_upload)