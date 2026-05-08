from sqlite3 import IntegrityError

import pytest

from app.courts import dao
from test.test_base import test_client,test_session, test_app, mock_cloudinary,setup_booking_data


def test_view_cac_trang_thong_tin_tinh(test_client):
    assert test_client.get('/').status_code == 200
    assert test_client.get('/dieu-khoan').status_code == 200
    assert test_client.get('/gioi-thieu').status_code == 200

def test_cap_nhat_ho_so_thanh_cong(test_session, setup_booking_data):
    dao.update_profile(setup_booking_data['user'].id, name="Khách Vip", phone="0123123123", email="vip@gmail.com")

    assert setup_booking_data['user'].ho_ten == "Khách Vip"
    assert setup_booking_data['user'].so_dien_thoai == "0123123123"


def test_cap_nhat_ho_so_kem_avatar(test_session, setup_booking_data, monkeypatch):
    monkeypatch.setattr('cloudinary.uploader.upload', lambda x: {'secure_url': 'https://link-anh-moi.com'})

    dao.update_profile(setup_booking_data['user'].id, "Khách", "0111111111", "khach@gmail.com", avatar="file_anh_gia")

    assert setup_booking_data['user'].avatar == 'https://link-anh-moi.com'


def test_loi_cap_nhat_ho_so_trung_thong_tin(test_session, setup_booking_data):
    with pytest.raises(Exception) as loi_email:
        dao.update_profile(setup_booking_data['user'].id, "Khách", "0111111111", "admin@gmail.com")
    assert "Email này đã được sử dụng" in str(loi_email.value)

    with pytest.raises(Exception) as loi_sdt:
        dao.update_profile(setup_booking_data['user'].id, "Khách", "0999999999", "khach@gmail.com")
    assert "Số điện thoại này đã được sử dụng" in str(loi_sdt.value)


def test_dao_cap_nhat_ho_so_nguoi_dung_khong_ton_tai(test_session):
    with pytest.raises(Exception) as e:
        dao.update_profile(user_id=9999, name="Ẩn", phone="0001234565", email="no-user@gmail.com")

    assert "Người dùng không tồn tại!" in str(e.value)

def test_loi_database_khi_cap_nhat_ho_so(test_session, setup_booking_data, monkeypatch):
    def fake_commit():
        raise IntegrityError("Lỗi DB")

    monkeypatch.setattr('app.extention.db.session.commit', fake_commit)

    with pytest.raises(Exception) as loi_db:
        dao.update_profile(setup_booking_data['user'].id, "Khách", "0111111111", "khach@gmail.com")
    assert "Có lỗi xảy ra khi lưu dữ liệu" in str(loi_db.value)


def test_ho_so_ca_nhan_thanh_cong(test_client, setup_booking_data):
    test_client.post('/login', data={'username': 'khach', 'password': '123456'})

    response = test_client.post('/profile', data={
        'name': 'Nguyễn J', 'phone': '0123456789', 'email': 'khach123@gmail.com'
    })

    assert response.status_code == 302
    assert '/profile' in response.headers['Location']


def test_ho_so_ca_nhan_loi_thieu_thong_tin(test_client, setup_booking_data):
    test_client.post('/login', data={'username': 'khach', 'password': '123456'})

    response = test_client.post('/profile', data={'name': 'A', 'phone': '', 'email': 'a@gmail.com'})
    html = response.data.decode('utf-8')

    assert "Vui lòng không để trống" in html


def test_ho_so_ca_nhan_loi_trung_thong_tin(test_client, setup_booking_data):
    test_client.post('/login', data={'username': 'khach', 'password': '123456'})

    response = test_client.post('/profile', data={'name': 'A', 'phone': '0111111111', 'email': 'admin@gmail.com'})
    html = response.data.decode('utf-8')

    assert "Email này đã được sử dụng" in html