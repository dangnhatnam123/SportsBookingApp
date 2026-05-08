from unittest.mock import patch, MagicMock
from test.test_base import test_app

def test_process_payment_success(test_app):
    client = test_app.test_client()
    with patch('flask_login.utils._get_user') as mock_user:
        mock_user.return_value = MagicMock(id=1, is_authenticated=True)
        with patch('app.booking.dao.luu_dat_san') as mock_save:
            mock_save.return_value = MagicMock()
            response = client.post('/process-payment', data={
                'san_id': '1', 'ngay': '2026-05-20', 'gio_bd': '17:00',
                'gio_kt': '19:00', 'tong_tien': '200000'
            }, follow_redirects=True)
            assert response.status_code == 200
            assert "Đặt sân thành công!" in response.data.decode('utf-8')

def test_process_payment_fail(test_app):
    client = test_app.test_client()
    with patch('flask_login.utils._get_user') as mock_user:
        mock_user.return_value = MagicMock(id=1, is_authenticated=True)
        with patch('app.booking.dao.luu_dat_san') as mock_save:
            mock_save.return_value = False
            response = client.post('/process-payment', data={
                'san_id': '1', 'ngay': '2026-05-20', 'gio_bd': '17:00',
                'gio_kt': '19:00', 'tong_tien': '200000'
            }, follow_redirects=False)
            assert response.status_code == 302
            assert "/search" in response.location

def test_process_payment_momo_redirect_to_payurl(test_app):
    client = test_app.test_client()
    with patch('flask_login.utils._get_user') as mock_user:
        mock_user.return_value = MagicMock(id=1, is_authenticated=True)
        with patch('app.booking.dao.luu_dat_san') as mock_save:
            mock_save.return_value = MagicMock(id=123)
            with patch('requests.post') as mock_post:
                mock_post.return_value.json.return_value = {
                    'resultCode': 0,
                    'payUrl': 'https://test-payment.momo.vn/pay/example'
                }
                response = client.post('/process-payment', data={
                    'san_id': '1', 'ngay': '2026-05-20', 'gio_bd': '17:00',
                    'gio_kt': '19:00', 'tong_tien': '200000',
                    'payment_method': 'momo'
                }, follow_redirects=False)
                assert response.status_code == 302
                assert response.location == 'https://test-payment.momo.vn/pay/example'

def test_process_payment_momo_error_redirect(test_app):
    client = test_app.test_client()
    with patch('flask_login.utils._get_user') as mock_user:
        mock_user.return_value = MagicMock(id=1, is_authenticated=True)
        with patch('app.booking.dao.luu_dat_san') as mock_save:
            mock_save.return_value = MagicMock(id=99)
            with patch('requests.post') as mock_post:
                mock_post.return_value.json.return_value = {'resultCode': 99}
                response = client.post('/process-payment', data={
                    'san_id': '1', 'ngay': '2026-05-20', 'gio_bd': '17:00',
                    'gio_kt': '19:00', 'tong_tien': '200000', 'payment_method': 'momo'
                }, follow_redirects=False)
                assert response.status_code == 302
                assert "/search" in response.location

def test_process_payment_momo_exception_redirect(test_app):
    client = test_app.test_client()
    with patch('flask_login.utils._get_user') as mock_user:
        mock_user.return_value = MagicMock(id=1, is_authenticated=True)
        with patch('app.booking.dao.luu_dat_san') as mock_save:
            mock_save.return_value = MagicMock(id=99)
            with patch('requests.post', side_effect=Exception("Lỗi kết nối")):
                response = client.post('/process-payment', data={
                    'san_id': '1', 'ngay': '2026-05-20', 'gio_bd': '17:00',
                    'gio_kt': '19:00', 'tong_tien': '200000', 'payment_method': 'momo'
                }, follow_redirects=False)
                assert response.status_code == 302
                assert "/search" in response.location

def test_checkout_view_missing_params_redirect(test_app):
    client = test_app.test_client()
    with patch('flask_login.utils._get_user') as mock_user:
        mock_user.return_value = MagicMock(id=1, is_authenticated=True)
        response = client.get('/checkout/1', follow_redirects=False)
        assert response.status_code == 302
        assert "/search" in response.location