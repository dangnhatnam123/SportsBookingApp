import pytest
from unittest.mock import patch, MagicMock
from app.test.test_base import test_app, test_session

def test_process_payment_success(test_app):
    client = test_app.test_client()

    with patch('flask_login.utils._get_user') as mock_user:
        mock_user.return_value = MagicMock(id=1, is_authenticated=True)

        with patch('app.booking.dao.luu_dat_san') as mock_save:
            mock_save.return_value = True

            response = client.post('/process-payment', data={
                'san_id': '1',
                'ngay': '2026-05-20',
                'gio_bd': '17:00',
                'gio_kt': '19:00',
                'tong_tien': '200000'
            })

            assert response.status_code == 200
            # Giải mã binary sang string để check tiếng Việt
            assert "Thanh toán thành công!" in response.data.decode('utf-8')

def test_process_payment_fail(test_app):
    client = test_app.test_client()

    with patch('flask_login.utils._get_user') as mock_user:
        mock_user.return_value = MagicMock(id=1, is_authenticated=True)

        with patch('app.booking.dao.luu_dat_san') as mock_save:
            mock_save.return_value = False

            response = client.post('/process-payment', data={
                'san_id': '1',
                'ngay': '2026-05-20',
                'gio_bd': '17:00',
                'gio_kt': '19:00',
                'tong_tien': '200000'
            })

            assert response.status_code == 200
            assert "Có lỗi xảy ra" in response.data.decode('utf-8')