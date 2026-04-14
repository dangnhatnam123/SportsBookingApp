from app.booking.dao import huy_dat_san
from app.test.test_base import test_session, test_app
from app.models import DatLich, HoaDon, TrangThaiDL, TrangThaiHoaDon
from datetime import date, time, datetime, timedelta
import pytest

# tét hủy sân thành công
def test_success(test_session,test_app):
    ngay_mai = datetime.now() + timedelta(days=1)
    dl = DatLich(
        ngay_choi=ngay_mai.date(),
        gio_bd=time(18, 0),
        gio_kt=time(19, 0),
        ma_nd=1,
        ma_san=1,
        trang_thai=TrangThaiDL.CHUA_HOAN_THANH
    )
    test_session.add(dl)
    test_session.commit()

    hd = HoaDon(
        tong_tien=150000,
        trang_thai=TrangThaiHoaDon.CHUA_THANH_TOAN,
        ma_dat=dl.id
    )
    test_session.add(hd)
    test_session.commit()

    ma_dl = dl.id
    ma_hd = hd.id

    result = huy_dat_san(ma_dat_san=ma_dl)

    dl_after = DatLich.query.filter(DatLich.id.__eq__(ma_dl)).first()
    hd_after = HoaDon.query.filter(HoaDon.id.__eq__(ma_hd)).first()

    assert result is True
    assert dl_after is not None
    assert dl_after.trang_thai == TrangThaiDL.DA_HUY
    assert hd_after is not None
    assert hd_after.trang_thai == TrangThaiHoaDon.DA_HUY



#tét ID không ồn tại
@pytest.mark.parametrize('invalid_id', [
    0, -1, 999999
])
def test_invalid_id(test_session, invalid_id, test_app):
    result = huy_dat_san(ma_dat_san=invalid_id)

    assert result is False

#test hủy sân khi đã đá xong
def test_cancel_completed_booking(test_session, test_app):
    ngay_mai = datetime.now() + timedelta(days=1)
    dl = DatLich(
        ngay_choi=ngay_mai.date(),
        gio_bd=time(18, 0),
        gio_kt=time(19, 0),
        ma_nd=1,
        ma_san=1,
        trang_thai=TrangThaiDL.DA_HOAN_THANH)
    test_session.add(dl)
    test_session.commit()

    with pytest.raises(ValueError) as error_info:
        huy_dat_san(ma_dat_san=dl.id)

    assert str(error_info.value) == "Sân đã đá xong, không thể hủy!"

#test hủy đơn hàng chính chủ
def test_cancel_wrong_user(test_session, test_app):
    ngay_mai = datetime.now() + timedelta(days=1)
    dl = DatLich(
        ngay_choi=ngay_mai.date(),
        gio_bd=time(10, 0),
        gio_kt=time(11, 0),
        ma_nd=1,
        ma_san=1,
        trang_thai=TrangThaiDL.CHUA_HOAN_THANH
    )
    test_session.add(dl)
    test_session.commit()

    with pytest.raises(ValueError) as error_info:
        huy_dat_san(ma_dat_san=dl.id, user_id=99)

    assert "không có quyền" in str(error_info.value)

#tét lỗi đặt khi còn ít hơn 2 tineegs
def test_cancel_too_close_to_time(test_session, test_app):
    now = datetime.now()
    thoi_gian_da = now + timedelta(hours=1)

    dl = DatLich(
        ngay_choi=thoi_gian_da.date(),
        gio_bd=thoi_gian_da.time(),
        gio_kt=(thoi_gian_da + timedelta(hours=1)).time(),
        ma_nd=1,
        ma_san=1,
        trang_thai=TrangThaiDL.CHUA_HOAN_THANH
    )
    test_session.add(dl)
    test_session.commit()

    with pytest.raises(ValueError) as error_info:
        huy_dat_san(ma_dat_san=dl.id, user_id=1)

    assert "ít nhất 2 tiếng" in str(error_info.value)