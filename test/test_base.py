import pytest
from flask import Flask
from app import db, login_manager
from app.auth.views import auth_bp
from app.booking.views import booking_bp
from app.courts.views import courts_bp


def create_app():
    app = Flask(__name__, template_folder='../app/templates', static_folder='../app/static')
    app.config.update({
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "PAGE_SIZE": 2,
        "TESTING": True,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": '34y394yjsbdkjsdjksdh'
    })

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(courts_bp)

    return app


@pytest.fixture(scope='session')
def test_app():
    app = create_app()
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def test_client(test_app):
    return test_app.test_client()


@pytest.fixture
def test_session(test_app):
    with test_app.app_context():
        db.session.remove()
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
        yield db.session
        db.session.rollback()
        db.session.remove()


@pytest.fixture
def mock_cloudinary(monkeypatch):
    def fake_upload(file, **kwargs):
        return {'secure_url': 'https://fake-avatar.png'}

    monkeypatch.setattr('cloudinary.uploader.upload', fake_upload)