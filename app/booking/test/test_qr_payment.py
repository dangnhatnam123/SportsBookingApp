import pytest
from unittest.mock import MagicMock, patch
from flask import Flask
from app import db  # Import db từ project của bà
from app.booking.views import booking_bp


@pytest.fixture
def client():
    test_app = Flask(__name__)
    test_app.config['TESTING'] = True
    test_app.config['WTF_CSRF_ENABLED'] = False

    test_app.config['SECRET_KEY'] = 'mot-cai-ma-bi-mat-nao-do'

    test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    test_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(test_app)
    test_app.register_blueprint(booking_bp, url_prefix='/booking')

    with test_app.test_client() as client:
        with test_app.app_context():
            yield client

@patch('app.booking.dao.get_san_by_id')
@patch('app.booking.dao.luu_dat_san')
@patch('flask_login.utils._get_user')
def test_payment_fail_db(mock_get_user, mock_luu_dat, mock_get_san, client):

    mock_user = MagicMock(id=1, is_authenticated=True)
    mock_get_user.return_value = mock_user

    mock_get_san.return_value = MagicMock(ten_san="Sân Test")

    mock_luu_dat.return_value = None

    payload = {
        'san_id': '1',
        'payment_method': 'momo',
        'ngay': '2026-05-14', 'gio_bd': '14:00', 'gio_kt': '16:00', 'tong_tien': '200000'
    }

    response = client.post('/booking/process-payment', data=payload)

    assert response.status_code == 302
    assert mock_luu_dat.called