import pytest
from datetime import datetime, date, time
from app.booking import dao
from app.models import San, DatLich, HoaDon, TrangThaiDL, TrangThaiHoaDon, LoaiSan
from app.test.test_base import test_session, test_app


def test_luu_dat_san_success(test_session, test_app):
    s = San(ten_san="Sân Test Transaction",
            active=True,
            gia_san_theo_gio=100000,
            loai_san=LoaiSan.BONG_DA)
    test_session.add(s)
    test_session.commit()

    result = dao.luu_dat_san(
        ma_nd=1,
        ma_san=s.id,
        ngay_choi="2026-12-30",
        gio_bd="18:00",
        gio_kt="20:00",
        tong_tien="200000"
    )

    assert result is True

    dl = DatLich.query.filter_by(ma_san=s.id).first()
    assert dl is not None
    assert dl.ngay_choi == date(2026, 12, 30)

    hd = HoaDon.query.filter_by(ma_dat=dl.id).first()
    assert hd is not None
    assert hd.tong_tien == 200000.0
    assert hd.trang_thai == TrangThaiHoaDon.DA_THANH_TOAN


def test_luu_dat_san_fail_format(test_session, test_app):
    result = dao.luu_dat_san(
        ma_nd=1,
        ma_san=1,
        ngay_choi="30/12/2026",
        gio_bd="18:00",
        gio_kt="20:00",
        tong_tien="200000"
    )

    assert result is False

    assert DatLich.query.count() == 0