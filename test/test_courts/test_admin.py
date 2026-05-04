import pytest
from datetime import datetime, timedelta
from app.models import San, DatLich, NguoiDung, VaiTro
from app.courts import dao
import hashlib
from unittest.mock import patch
from test.test_base import test_client,test_session,test_app ,mock_cloudinary


def test_add_va_load_san(test_session, test_app):
    dao.add_san_moi(ten="Sân 1", loai="BONG_DA", gia_thue=100000)
    dao.add_san_moi(ten="Sân 2", loai="TENNIS", gia_thue=200000)
    danh_sach = dao.load_all_san()
    assert len(danh_sach) == 2
    assert any(s.ten_san == "Sân 1" for s in danh_sach)
    assert any(s.ten_san == "Sân 2" for s in danh_sach)


def test_getID_san(test_session, test_app):
    dao.add_san_moi(ten="Sân", loai="CAU_LONG", gia_thue=50000)
    san = test_session.query(San).first()
    san_tim_thay = dao.get_san(san.id)
    assert san_tim_thay is not None
    assert san_tim_thay.ten_san == "Sân"
    assert dao.get_san(9999) is None

def test_update_san(test_session, test_app):
    dao.add_san_moi(ten="Sân Cũ", loai="BONG_DA", gia_thue=100000)
    san = test_session.query(San).first()

    dao.update_san(san.id, ten="Sân Mới", loai="TENNIS", gia_san_theo_gio=150000)

    san_da_update = test_session.get(San, san.id)
    assert san_da_update.ten_san == "Sân Mới"
    assert san_da_update.loai_san.name == "TENNIS"
    dao.update_san(9999, "Test", "TEST", 0)


def test_xoa_san(test_session, test_app):
    dao.add_san_moi(ten="Sân 1", loai="BONG_DA", gia_thue=100000)
    san = test_session.query(San).first()
    dao.xoa_san(san.id)
    assert test_session.get(San, san.id) is None


def test_check_ten_san_trung_lap(test_session, test_app):
    dao.add_san_moi(ten="Sân Chảo Lửa", loai="BONG_DA", gia_thue=100000)
    san = test_session.query(San).first()

    assert dao.check_ten_san("Sân Chảo Lửa") is True
    assert dao.check_ten_san("Sân No") is False
    assert dao.check_ten_san("Sân Chảo Lửa", exclude_id=san.id) is False


def test_kiem_tra_lich_dat_truoc_khi_xoa_san(test_session, test_app):
    dao.add_san_moi(ten="Sân 35", loai="BONG_DA", gia_thue=100000)
    san = test_session.query(San).first()

    assert dao.kiem_tra_lich_dat(san.id) is False

    ngay_mai = datetime.now().date() + timedelta(days=1)
    lich = DatLich(ma_san=san.id, ma_nd=1, ngay_choi=ngay_mai, gio_bd=datetime.now().time(), gio_kt=datetime.now().time())
    test_session.add(lich)
    test_session.commit()

    assert dao.kiem_tra_lich_dat(san.id) is True


@pytest.fixture
def admin_login(test_client, test_session):
    pw = str(hashlib.md5('123456'.encode('utf-8')).hexdigest())
    admin = NguoiDung(ho_ten="Admin", ten_nd="admin", mat_khau=pw, vai_tro=VaiTro.QUAN_LY)
    test_session.add(admin)
    test_session.commit()
    test_client.post('/login', data={'username': 'admin', 'password': '123456'})


@pytest.fixture
def san_co_lich_ngay_mai(test_session):
    dao.add_san_moi(ten="Sân Đặt", loai="BONG_DA", gia_thue=100000)
    san_moi = test_session.query(San).first()
    ngay_mai = datetime.now().date() + timedelta(days=1)
    lich = DatLich(ma_san=san_moi.id, ma_nd=1, ngay_choi=ngay_mai, gio_bd=datetime.now().time(), gio_kt=datetime.now().time())
    test_session.add(lich)
    test_session.commit()
    return san_moi

def test_home_route(test_client):
    res = test_client.get('/')
    assert res.status_code == 200


def test_dieu_khoan_route(test_client):
    res = test_client.get('/dieu-khoan')
    assert res.status_code == 200


def test_gioi_thieu_route(test_client):
    res = test_client.get('/gioi-thieu')
    assert res.status_code == 200


def test_manage_san_thanh_cong(test_client, test_session, admin_login):
    san_moi = San(ten_san="Sân Test Manage", loai_san="BONG_DA", gia_san_theo_gio=100000)
    test_session.add(san_moi)
    test_session.commit()

    res = test_client.get('/admin/manage_san')
    assert res.status_code == 200
    assert "Sân Test Manage" in res.data.decode('utf-8')


def test_manage_san_exception(test_client, test_session, admin_login):
    with patch('app.courts.views.dao.load_all_san') as mock_load:
        mock_load.side_effect = Exception("Lỗi DB Giả Lập")

        res = test_client.get('/admin/manage_san')
        assert res.status_code == 200


def test_add_san_thanh_cong(test_client, test_session, admin_login):
    res = test_client.post('/admin/add-san', data={
        'ten_san': 'Sân Bóng',
        'loai_san': 'BONG_DA',
        'gia': 150000
    }, follow_redirects=True)

    assert "Thêm sân thành công" in res.data.decode('utf-8')

    san_trong_db = test_session.query(San).filter_by(ten_san='Sân Bóng').first()
    assert san_trong_db is not None
    assert san_trong_db.gia_san_theo_gio == 150000


def test_add_san_trung_ten(test_client, test_session, admin_login):
    san_moi = San(ten_san="Sân Trùng", loai_san="BONG_DA", gia_san_theo_gio=100000)
    test_session.add(san_moi)
    test_session.commit()

    res = test_client.post('/admin/add-san', data={
        'ten_san': 'Sân Trùng',
        'loai_san': 'TENNIS',
        'gia': 200000
    }, follow_redirects=True)

    assert "đã tồn tại trong hệ thống" in res.data.decode('utf-8')

    so_luong = test_session.query(San).filter_by(ten_san='Sân Trùng').count()
    assert so_luong == 1


def test_add_san_exception(test_client, test_session, admin_login):
    with patch('app.courts.views.dao.add_san_moi') as mock_add:
        mock_add.side_effect = Exception("Lỗi DB Giả Lập")

        res = test_client.post('/admin/add-san', data={
            'ten_san': 'Sân Lỗi', 'loai_san': 'BONG_DA', 'gia': 100
        }, follow_redirects=True)

        assert "thêm sân thất bại" in res.data.decode('utf-8')


def test_delete_san_thanh_cong(test_client, test_session, admin_login):
    san_moi = San(ten_san="Sân xóa", loai_san="BONG_DA", gia_san_theo_gio=100000)
    test_session.add(san_moi)
    test_session.commit()
    san_id = san_moi.id

    res = test_client.post(f'/admin/delete-san/{san_id}', follow_redirects=True)

    assert "Đã xóa sân thành công!" in res.data.decode('utf-8')
    assert test_session.get(San, san_id) is None

def test_delete_san_co_lich_dat(test_client, test_session, admin_login, san_co_lich_ngay_mai):
    san_id = san_co_lich_ngay_mai.id

    res = test_client.post(f'/admin/delete-san/{san_id}', follow_redirects=True)

    assert "Sân đã có lịch đặt trong tương lai" in res.data.decode('utf-8')
    assert test_session.get(San, san_id) is not None


def test_delete_san_exception(test_client, test_session, admin_login):
    san_moi = San(ten_san="Sân Test Xóa Lỗi", loai_san="BONG_DA", gia_san_theo_gio=100)
    test_session.add(san_moi)
    test_session.commit()

    with patch('app.courts.views.dao.xoa_san') as mock_xoa:
        mock_xoa.side_effect = Exception("Lỗi DB Giả Lập")
        res = test_client.post(f'/admin/delete-san/{san_moi.id}', follow_redirects=True)
        assert "Lỗi hệ thống" in res.data.decode('utf-8')

def test_edit_san_thanh_cong(test_client, test_session, admin_login):
    san_moi = San(ten_san="Sân Cũ", loai_san="BONG_DA", gia_san_theo_gio=100000)
    test_session.add(san_moi)
    test_session.commit()

    res = test_client.post(f'/admin/edit-san/{san_moi.id}', data={
        'ten_san': 'Sân Mới Đã Sửa',
        'loai_san': 'TENNIS',
        'gia': 250000
    }, follow_redirects=True)

    assert "Cập nhật thông tin sân thành công" in res.data.decode('utf-8')

    san_sau_sua = test_session.get(San, san_moi.id)
    assert san_sau_sua.ten_san == 'Sân Mới Đã Sửa'
    assert san_sau_sua.gia_san_theo_gio == 250000


def test_edit_san_exception(test_client, test_session, admin_login):
    san_moi = San(ten_san="Sân Test Sửa Lỗi", loai_san="BONG_DA", gia_san_theo_gio=100)
    test_session.add(san_moi)
    test_session.commit()

    with patch('app.courts.views.dao.update_san') as mock_update:
        mock_update.side_effect = Exception("Lỗi DB Giả Lập")

        res = test_client.post(f'/admin/edit-san/{san_moi.id}', data={
            'ten_san': 'Tên Mới', 'loai_san': 'BONG_DA', 'gia': 200
        }, follow_redirects=True)
        assert "Lỗi cập nhật" in res.data.decode('utf-8')


def test_edit_san_trung_ten(test_client, test_session, admin_login):
    san_1 = San(ten_san="Sân A", loai_san="BONG_DA", gia_san_theo_gio=100000)
    san_2 = San(ten_san="Sân B", loai_san="TENNIS", gia_san_theo_gio=200000)
    test_session.add_all([san_1, san_2])
    test_session.commit()

    res = test_client.post(f'/admin/edit-san/{san_1.id}', data={
        'ten_san': 'Sân B',
        'loai_san': 'BONG_DA',
        'gia': 100000
    }, follow_redirects=True)

    assert "đã được sử dụng" in res.data.decode('utf-8')

    san_1_kiem_tra = test_session.get(San, san_1.id)
    assert san_1_kiem_tra.ten_san == "Sân A"

