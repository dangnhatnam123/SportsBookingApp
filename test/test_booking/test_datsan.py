import hashlib
from datetime import datetime, timedelta
import pytest
from test.test_base import test_client, test_session, test_app
from app.booking import dao
from app.models import NguoiDung, San, VaiTro, LoaiSan

@pytest.fixture()
def setup_booking_data(test_session):
    pw = str(hashlib.md5('123456'.encode('utf-8')).hexdigest())
    u = NguoiDung(ho_ten="Khach Dat San", ten_nd="khach", mat_khau=pw, vai_tro=VaiTro.NGUOI_DUNG)
    s1 = San(ten_san="Sân Chảo Lửa 1", loai_san=LoaiSan.BONG_DA, gia_san_theo_gio=100000, active=True)
    s2 = San(ten_san="Sân Chảo Lửa 2", loai_san=LoaiSan.BONG_DA, gia_san_theo_gio=100000, active=True)
    test_session.add_all([u, s1, s2])
    test_session.commit()
    return {'user': u, 'san1': s1, 'san2': s2}

def test_dat_san_trong_qua_khu(test_client):
    ngay_qua_khu = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    res = test_client.get(f'/search?ngay={ngay_qua_khu}&gio_bd=10:00&gio_kt=11:00')
    assert "Lỗi: Không thể tìm sân trong quá khứ!" in res.data.decode('utf-8')

def test_search_gio_qua_khu_trong_ngay(test_client):
    now = datetime.now()
    hom_nay_str = now.strftime('%Y-%m-%d')
    res = test_client.get(f'/search?ngay={hom_nay_str}&gio_bd=00:00&gio_kt=01:00')
    assert res.status_code == 200

def test_view_search_loi_thoi_gian(test_client):
    res = test_client.get('/search?ngay=2026-12-12&gio_bd=10:00&gio_kt=09:00')
    assert 'Lỗi: Giờ kết thúc phải lớn hơn giờ bắt đầu!' in res.data.decode('utf-8')

def test_dat_san_duoi_1_tieng(test_client):
    ngay_mai = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    res = test_client.get(f'/search?ngay={ngay_mai}&gio_bd=10:00&gio_kt=10:30')
    assert "Lỗi: Thời gian thuê tối thiểu phải là 1 tiếng!" in res.data.decode('utf-8')

def test_dat_san_chua_dang_nhap(test_client, setup_booking_data):
    res = test_client.get(f'/checkout/{setup_booking_data["san1"].id}?ngay=2025-12-12&gio_bd=10:00&gio_kt=11:00')
    assert res.status_code == 302
    assert '/login' in res.headers['Location']

def test_toi_da_3_san_ngay(test_client, setup_booking_data, test_session):
    test_client.post('/login', data={'username': 'khach', 'password': '123456'})
    ngay_mai = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    for i in range(3):
        dao.luu_dat_san(
            ma_nd=setup_booking_data['user'].id,
            ma_san=setup_booking_data['san1'].id,
            ngay_choi=ngay_mai,
            gio_bd=f'{7 + i:02d}:00',
            gio_kt=f'{8 + i:02d}:00',
            tong_tien=100000
        )
    res = test_client.get(f'/checkout/{setup_booking_data["san2"].id}?ngay={ngay_mai}&gio_bd=18:00&gio_kt=19:00')
    assert res.status_code == 200
    assert "tối đa 3 sân một ngày" in res.data.decode('utf-8')

def test_khong_hien_thi_san_da_co_nguoi_dat(test_client, setup_booking_data):
    ngay_mai = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    dao.luu_dat_san(ma_nd=999, ma_san=setup_booking_data['san1'].id, ngay_choi=ngay_mai,
                    gio_bd='15:00', gio_kt='16:00', tong_tien=100000)
    res = test_client.get(f'/search?ngay={ngay_mai}&gio_bd=15:00&gio_kt=16:00')
    assert setup_booking_data['san1'].ten_san not in res.data.decode('utf-8')

def test_get_history_co_page(test_session, setup_booking_data):
    res, pages = dao.get_history_by_user(setup_booking_data['user'].id, page=1)
    assert isinstance(res, list)

def test_load_san_loai_san(test_session):
    res = dao.load_san_trong(loai_san_val="Bóng đá")
    assert isinstance(res, list)

def test_view_san_khong_ton_tai(test_client):
    res = test_client.get('/san/311')
    assert res.status_code == 404
    assert 'Không tìm thấy sân này!' in res.data.decode('utf-8')

def test_view_search_thanh_cong(test_client, setup_booking_data):
    san_id = setup_booking_data['san1'].id
    res = test_client.get(f'/san/{san_id}')
    assert res.status_code == 200
    assert setup_booking_data['san1'].ten_san in res.data.decode('utf-8')

def test_view_checkout_san_id_sai(test_client, setup_booking_data):
    test_client.post('/login', data={'username': 'khach', 'password': '123456'})
    res = test_client.get('/checkout/999?ngay=2026-12-12&gio_bd=10:00&gio_kt=11:00')
    assert res.status_code == 302
    assert res.headers['Location'].endswith('/search')