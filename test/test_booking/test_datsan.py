from datetime import datetime, timedelta

from app.models import LoaiSan
from test.test_base import test_client,test_session, test_app,setup_booking_data
from app.booking import dao


def test_dao_dem_so_luong_san_theo_ten(test_session, setup_booking_data):
    so_luong = dao.count_san_trong(ten_san_val="Chảo Lửa 1")
    assert so_luong == 1

def test_tim_kiem_san_trong_thanh_cong(test_session, setup_booking_data):
    ket_qua_loai = dao.load_san_trong(loai_san_val=LoaiSan.BONG_DA)
    ket_qua_ten = dao.load_san_trong(ten_san_val="Chảo Lửa 1")

    assert len(ket_qua_loai) >= 2
    assert len(ket_qua_ten) == 1
    assert ket_qua_ten[0].ten_san == "Sân Chảo Lửa 1"


def test_thuc_hien_dat_san_thanh_cong(test_session, setup_booking_data):
    dat_lich = dao.luu_dat_san(
        ma_nd=setup_booking_data['user'].id,
        ma_san=setup_booking_data['san1'].id,
        ngay_choi='2026-12-12',
        gio_bd='10:00',
        gio_kt='11:00',
        tong_tien=100000
    )

    assert dat_lich is not False
    assert dat_lich.ma_san == setup_booking_data['san1'].id
    assert dat_lich.trang_thai.name == 'CHUA_HOAN_THANH'


def test_luu_dat_san_bi_loi_database(test_session, setup_booking_data, monkeypatch):
    def fake_flush():
        raise Exception("Sập Database")

    monkeypatch.setattr('app.extention.db.session.flush', fake_flush)

    ket_qua = dao.luu_dat_san(
        ma_nd=setup_booking_data['user'].id, ma_san=setup_booking_data['san1'].id,
        ngay_choi='2026-12-12', gio_bd='10:00', gio_kt='11:00', tong_tien=100000
    )

    assert ket_qua is False

def test_rang_buoc_chua_dang_nhap_khong_cho_dat(test_client, setup_booking_data):
    response = test_client.get(f'/checkout/{setup_booking_data["san1"].id}?ngay=2026-12-12&gio_bd=10:00&gio_kt=11:00')

    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_mo_trang_xac_nhan_dat_san_thanh_cong(test_client, setup_booking_data):
    test_client.post('/login', data={'username': 'khach', 'password': '123456'})
    ngay_mai = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    response = test_client.get(f'/checkout/{setup_booking_data["san1"].id}?ngay={ngay_mai}&gio_bd=10:00&gio_kt=11:00')
    html = response.data.decode('utf-8')

    assert response.status_code == 200
    assert setup_booking_data['san1'].ten_san in html


def test_rang_buoc_vao_trang_xac_nhan_thieu_thong_tin(test_client, setup_booking_data):
    test_client.post('/login', data={'username': 'khach', 'password': '123456'})

    response = test_client.get(f'/checkout/{setup_booking_data["san1"].id}')

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/search')


def test_rang_buoc_xac_nhan_cho_san_khong_ton_tai(test_client, setup_booking_data):
    test_client.post('/login', data={'username': 'khach', 'password': '123456'})
    ngay_mai = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    response = test_client.get(f'/checkout/9999?ngay={ngay_mai}&gio_bd=10:00&gio_kt=11:00')

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/search')


def test_rang_buoc_khong_cho_chon_ngay_qua_khu(test_client):
    ngay_hom_qua = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    response = test_client.get(f'/search?ngay={ngay_hom_qua}&gio_bd=10:00&gio_kt=11:00')
    html = response.data.decode('utf-8')

    assert "Lỗi: Không thể tìm sân trong quá khứ!" in html


def test_rang_buoc_khong_cho_chon_gio_qua_khu_trong_ngay(test_client):
    hom_nay = datetime.now().strftime('%Y-%m-%d')
    gio_da_qua = "00:00"

    response = test_client.get(f'/search?ngay={hom_nay}&gio_bd={gio_da_qua}&gio_kt=23:00')
    html = response.data.decode('utf-8')

    assert 'không được chọn giờ trong quá khứ' in html


def test_rang_buoc_thoi_gian_thue_toi_thieu_mot_tieng(test_client):
    ngay_mai = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    response = test_client.get(f'/search?ngay={ngay_mai}&gio_bd=10:00&gio_kt=10:30')
    html = response.data.decode('utf-8')

    assert "Lỗi: Thời gian thuê tối thiểu phải là 1 tiếng!" in html


def test_rang_buoc_gio_ket_thuc_sai_logic(test_client):
    ngay_mai = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    response = test_client.get(f'/search?ngay={ngay_mai}&gio_bd=10:00&gio_kt=09:00')
    html = response.data.decode('utf-8')

    assert 'Lỗi: Giờ kết thúc phải lớn hơn giờ bắt đầu!' in html


def test_rang_buoc_toi_da_ba_san_mot_ngay(test_client, setup_booking_data, test_session):
    test_client.post('/login', data={'username': 'khach', 'password': '123456'})
    ngay_mai = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    for i in range(3):
        gio_bd = f'{7 + i:02d}:00'
        gio_kt = f'{8 + i:02d}:00'
        dao.luu_dat_san(
            ma_nd=setup_booking_data['user'].id, ma_san=setup_booking_data['san1'].id,
            ngay_choi=ngay_mai, gio_bd=gio_bd, gio_kt=gio_kt, tong_tien=100000
        )

    response = test_client.get(f'/checkout/{setup_booking_data["san2"].id}?ngay={ngay_mai}&gio_bd=18:00&gio_kt=19:00')
    html = response.data.decode('utf-8')

    assert response.status_code == 200
    assert "tối đa 3 sân một ngày" in html


def test_rang_buoc_an_san_da_co_nguoi_dat(test_client, setup_booking_data):
    ngay_mai = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    dao.luu_dat_san(ma_nd=999, ma_san=setup_booking_data['san1'].id, ngay_choi=ngay_mai,
                    gio_bd='15:00', gio_kt='16:00', tong_tien=100000)

    response = test_client.get(f'/search?ngay={ngay_mai}&gio_bd=15:00&gio_kt=16:00')
    html = response.data.decode('utf-8')

    assert setup_booking_data['san1'].ten_san not in html


def test_dat_san_thanh_cong(test_client, setup_booking_data):
    test_client.post('/login', data={'username': 'khach', 'password': '123456'})
    ngay_mai = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    form_dat_san = {
        'san_id': setup_booking_data['san1'].id,
        'ngay': ngay_mai,
        'gio_bd': '14:00',
        'gio_kt': '15:00',
        'tong_tien': '100000',
        'payment_method': 'truc_tiep'
    }

    response = test_client.post('/process-payment', data=form_dat_san)

    assert response.status_code == 302
    assert '/orders' in response.headers['Location']


def test_view_xem_chi_tiet_san_thanh_cong(test_client, setup_booking_data):
    san_id = setup_booking_data['san1'].id

    response = test_client.get(f'/san/{san_id}')
    html = response.data.decode('utf-8')

    assert response.status_code == 200
    assert setup_booking_data['san1'].ten_san in html
