from datetime import date, time
from unittest.mock import patch, MagicMock
import requests
from test.test_base import test_app

def test_history_view_success(test_app):
    client = test_app.test_client()
    with patch('flask_login.utils._get_user', return_value=MagicMock(id=1, is_authenticated=True)):
        h1 = MagicMock()
        h1.id = 1
        h1.ngay_choi = date(2026, 5, 20)
        h1.gio_bd = time(17, 0)
        h1.gio_kt = time(19, 0)
        h1.san.ten_san = "Sân Cỏ Cây"
        h1.san.hinh_anh = "img.jpg"
        h1.hoa_don.tong_tien = 200000.0

        with patch('app.booking.dao.get_history_by_user', return_value=([h1], 1)):
            response = client.get('/orders?page=1')
            assert response.status_code == 200
            data_str = response.data.decode('utf-8')
            assert "Sân Cỏ Cây" in data_str
            assert "20/05/2026" in data_str

def test_history_view_pagination(test_app):
    client = test_app.test_client()
    with patch('flask_login.utils._get_user', return_value=MagicMock(id=1, is_authenticated=True)):
        with patch('app.booking.dao.get_history_by_user', return_value=([], 5)) as mock_get:
            response = client.get('/orders?page=2')
            assert response.status_code == 200
            mock_get.assert_called_once_with(1, page=2)

def test_history_view_unauthorized(test_app):
    client = test_app.test_client()
    response = client.get('/orders')
    assert response.status_code == 302

def test_history_view_momo_success_full_flow(test_app):
    client = test_app.test_client()
    with patch('flask_login.utils._get_user', return_value=MagicMock(id=1, is_authenticated=True)):
        with patch('app.booking.dao.update_momo_trans_id') as mock_update:
            with patch('app.booking.dao.get_history_by_user', return_value=([], 1)):
                response = client.get('/orders?resultCode=0&orderId=BILL_88&transId=MOMO12345')
                assert response.status_code == 200
                mock_update.assert_called_once_with('88', 'MOMO12345')

def test_history_view_momo_fail_trigger_except_fixed(test_app):
    client = test_app.test_client()
    with patch('flask_login.utils._get_user', return_value=MagicMock(id=1, is_authenticated=True)):
        with patch('app.booking.dao.get_history_by_user', return_value=([], 1)):
            response = client.get('/orders?resultCode=1001&orderId=FAILNOSPLIT')
            assert response.status_code == 200

def test_history_view_momo_success_trigger_except_fixed(test_app):
    client = test_app.test_client()
    with patch('flask_login.utils._get_user', return_value=MagicMock(id=1, is_authenticated=True)):
        with patch('app.booking.dao.get_history_by_user', return_value=([], 1)):
            response = client.get('/orders?resultCode=0&orderId=SUCCESSSNOSPLIT&transId=123')
            assert response.status_code == 200

def test_history_view_momo_success_invalid_format_trigger_except(test_app):
    client = test_app.test_client()
    with patch('flask_login.utils._get_user', return_value=MagicMock(id=1, is_authenticated=True)):
        with patch('app.booking.dao.get_history_by_user', return_value=([], 1)):
            response = client.get('/orders?resultCode=0&orderId=NOSPLITHERE&transId=123')
            assert response.status_code == 200

def test_history_view_momo_fail_invalid_format_trigger_except(test_app):
    client = test_app.test_client()
    with patch('flask_login.utils._get_user', return_value=MagicMock(id=1, is_authenticated=True)):
        with patch('app.booking.dao.get_history_by_user', return_value=([], 1)):
            response = client.get('/orders?resultCode=1001&orderId=ERROR_FORMAT_NO_UNDERSCORE')
            assert response.status_code == 200

def test_process_huy_dat_momo_test_success(test_app):
    client = test_app.test_client()
    with patch('flask_login.utils._get_user', return_value=MagicMock(id=1, is_authenticated=True)):
        mock_dat = MagicMock(ma_nd=1, loai_thanh_toan='momo', momo_trans_id="MOMO_TEST_123",
                             trang_thai_hien_tai='Chưa bắt đầu', ngay_choi=date(2026, 12, 31), gio_bd=time(17, 0))
        with patch('app.models.DatLich.query') as mock_query:
            mock_query.get_or_404.return_value = mock_dat
            with patch('app.booking.dao.huy_dat_san', return_value=True):
                response = client.post('/huy-dat-san/1', follow_redirects=False)
                assert response.status_code == 302

def test_process_huy_dat_momo_refund_fail(test_app):
    client = test_app.test_client()
    with patch('flask_login.utils._get_user', return_value=MagicMock(id=1, is_authenticated=True)):
        mock_dat = MagicMock(ma_nd=1, loai_thanh_toan='momo', momo_trans_id="REAL_ID",
                             ngay_choi=date(2026, 12, 31), gio_bd=time(17, 0))
        mock_dat.hoa_don.tong_tien = 200000
        with patch('app.models.DatLich.query') as mock_query:
            mock_query.get_or_404.return_value = mock_dat
            with patch('requests.post') as mock_post:
                mock_post.return_value.json.return_value = {'resultCode': 99, 'message': 'Fail'}
                response = client.post('/huy-dat-san/1', follow_redirects=False)
                assert response.status_code == 302

def test_process_huy_dat_momo_refund_exception(test_app):
    client = test_app.test_client()
    with patch('flask_login.utils._get_user', return_value=MagicMock(id=1, is_authenticated=True)):
        mock_dat = MagicMock(ma_nd=1, loai_thanh_toan='momo', momo_trans_id="REAL_ID",
                             ngay_choi=date(2026, 12, 31), gio_bd=time(17, 0))
        mock_dat.hoa_don.tong_tien = 200000
        with patch('app.models.DatLich.query') as mock_query:
            mock_query.get_or_404.return_value = mock_dat
            with patch('requests.post', side_effect=Exception("Timeout")):
                response = client.post('/huy-dat-san/1', follow_redirects=False)
                assert response.status_code == 302

def test_process_huy_dat_momo_no_trans_id(test_app):
    client = test_app.test_client()
    with patch('flask_login.utils._get_user', return_value=MagicMock(id=1, is_authenticated=True)):
        mock_dat = MagicMock(ma_nd=1, loai_thanh_toan='momo', momo_trans_id=None,
                             ngay_choi=date(2026, 12, 31), gio_bd=time(17, 0))
        with patch('app.models.DatLich.query') as mock_query:
            mock_query.get_or_404.return_value = mock_dat
            response = client.post('/huy-dat-san/1', follow_redirects=False)
            assert response.status_code == 302