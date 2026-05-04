from unittest.mock import patch, MagicMock, PropertyMock
from datetime import datetime, timedelta, time
from test.test_base import test_app, test_session
from app.models import San, LoaiSan, DatLich, TrangThaiDL, VaiTro


def test_court_detail_khong_tim_thay(test_app):
    client = test_app.test_client()
    with patch('app.booking.dao.get_san_by_id', return_value=None):
        response = client.get('/san/999')
        assert response.status_code == 404

        assert "Không tìm thấy" in response.data.decode('utf-8')

@patch('flask_login.utils._get_user')
def test_checkout_hop_le_tinh_tien(mock_user, test_session, test_app):
    client = test_app.test_client()
    user_mock = MagicMock(id=1, is_authenticated=True)
    user_mock.vai_tro = VaiTro.NGUOI_DUNG
    mock_user.return_value = user_mock

    s = San(ten_san="Sân Test", active=True, gia_san_theo_gio=100000, loai_san=LoaiSan.BONG_DA)
    test_session.add(s)
    test_session.commit()

    with patch('app.booking.dao.count_dat_san_trong_ngay', return_value=1):
        response = client.get(f'/checkout/{s.id}?ngay=2026-10-10&gio_bd=17:00&gio_kt=19:00')
        assert response.status_code == 200

def test_checkout_khong_tim_thay_san(test_app):
    client = test_app.test_client()
    with patch('flask_login.utils._get_user') as mock_user:
        mock_user.return_value = MagicMock(id=1, is_authenticated=True)
        with patch('app.booking.dao.get_san_by_id', return_value=None):
            response = client.get('/checkout/999?ngay=2026-10-10&gio_bd=17:00&gio_kt=18:00')
            assert response.status_code == 302
            assert '/search' in response.headers['Location']


@patch('flask_login.utils._get_user')
def test_view_huy_dat_san_cac_kich_ban_flash(mock_user, test_session, test_app):
    client = test_app.test_client()
    user_mock = MagicMock(id=1, is_authenticated=True)
    mock_user.return_value = user_mock

    ngay_xa = datetime.now() + timedelta(days=5)
    dl_ok = DatLich(ma_nd=1, ma_san=1, ngay_choi=ngay_xa.date(), gio_bd=time(10, 0), gio_kt=time(12, 0),
                    trang_thai=TrangThaiDL.CHUA_HOAN_THANH)
    test_session.add(dl_ok)
    test_session.commit()
    with patch('app.booking.dao.huy_dat_san', return_value=True):
        res = client.post(f'/huy-dat-san/{dl_ok.id}')
        assert res.status_code == 302

    dl_sai = DatLich(ma_nd=99, ma_san=1, ngay_choi=ngay_xa.date(), gio_bd=time(14, 0), gio_kt=time(15, 0),
                     trang_thai=TrangThaiDL.CHUA_HOAN_THANH)
    test_session.add(dl_sai)
    test_session.commit()
    res = client.post(f'/huy-dat-san/{dl_sai.id}')
    assert res.status_code == 302

    with patch('app.models.DatLich.trang_thai_hien_tai', new_callable=PropertyMock) as mock_status:
        mock_status.return_value = 'Sân đang được sử dụng'
        dl_da = DatLich(ma_nd=1, ma_san=1, ngay_choi=ngay_xa.date(), gio_bd=time(8, 0), gio_kt=time(9, 0),
                        trang_thai=TrangThaiDL.CHUA_HOAN_THANH)
        test_session.add(dl_da)
        test_session.commit()
        res = client.post(f'/huy-dat-san/{dl_da.id}')
        assert res.status_code == 302

    hom_qua = datetime.now() - timedelta(days=1)
    dl_past = DatLich(ma_nd=1, ma_san=1, ngay_choi=hom_qua.date(), gio_bd=time(10, 0), gio_kt=time(11, 0),
                      trang_thai=TrangThaiDL.CHUA_HOAN_THANH)
    test_session.add(dl_past)
    test_session.commit()
    res = client.post(f'/huy-dat-san/{dl_past.id}')
    assert res.status_code == 302

    now = datetime.now()
    dl_sat = DatLich(ma_nd=1, ma_san=1, ngay_choi=now.date(), gio_bd=(now + timedelta(minutes=30)).time(),
                     gio_kt=(now + timedelta(hours=1)).time(), trang_thai=TrangThaiDL.CHUA_HOAN_THANH)
    test_session.add(dl_sat)
    test_session.commit()
    res = client.post(f'/huy-dat-san/{dl_sat.id}')
    assert res.status_code == 302

    with patch('app.booking.dao.huy_dat_san', return_value=False):
        res = client.post(f'/huy-dat-san/{dl_ok.id}')
        assert res.status_code == 302