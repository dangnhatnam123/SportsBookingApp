from datetime import date, time
import pytest
from unittest.mock import patch, MagicMock
from app.test.test_base import test_app

def test_history_view_success(test_app):
    client = test_app.test_client()

    with patch('flask_login.utils._get_user') as mock_user:
        mock_user.return_value = MagicMock(id=1, is_authenticated=True)

        h1 = MagicMock()
        h1.id = 1
        h1.ngay_choi = date(2026, 5, 20)
        h1.gio_bd = time(17, 0)
        h1.gio_kt = time(19, 0)
        h1.san.ten_san = "Sân Cỏ Cây"
        h1.san.hinh_anh = "img.jpg"
        h1.hoa_don.tong_tien = 200000.0

        h2 = MagicMock()
        h2.id = 2
        h2.ngay_choi = date(2026, 5, 21)
        h2.gio_bd = time(18, 0)
        h2.gio_kt = time(20, 0)
        h2.san.ten_san = "Sân Đại Học"
        h2.san.hinh_anh = "img2.jpg"
        h2.hoa_don.tong_tien = 300000.0

        mock_history = [h1, h2]
        mock_total_pages = 5

        with patch('app.booking.dao.get_history_by_user') as mock_get_history:
            mock_get_history.return_value = (mock_history, mock_total_pages)

            response = client.get('/orders?page=1')
            assert response.status_code == 200
            data_str = response.data.decode('utf-8')
            assert "Sân Cỏ Cây" in data_str
            assert "20/05/2026" in data_str

def test_history_view_pagination(test_app):
    client = test_app.test_client()

    with patch('flask_login.utils._get_user') as mock_user:
        mock_user.return_value = MagicMock(id=1, is_authenticated=True)

        with patch('app.booking.dao.get_history_by_user', return_value=([], 5)) as mock_get_history:
            response = client.get('/orders?page=2')

            assert response.status_code == 200
            mock_get_history.assert_called_once_with(1, page=2)

def test_history_view_unauthorized(test_app):
    client = test_app.test_client()
    response = client.get('/orders')
    assert response.status_code == 302