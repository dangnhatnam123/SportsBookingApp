from datetime import date, time
import pytest
from app.booking import dao
from app.models import DatLich, San, LoaiSan
from app.test.test_base import test_session, test_app


def test_get_history_by_user_success(test_session, test_app):
    s = San(ten_san="Sân History", active=True, loai_san=LoaiSan.BONG_DA)
    test_session.add(s)
    test_session.commit()

    user_id = 99

    d1 = DatLich(
        ma_nd=user_id,
        ma_san=s.id,
        ngay_choi=date(2026, 4, 15),
        gio_bd=time(17, 0),
        gio_kt=time(18, 0)
    )
    d2 = DatLich(
        ma_nd=user_id,
        ma_san=s.id,
        ngay_choi=date(2026, 4, 16),
        gio_bd=time(19, 0),
        gio_kt=time(20, 0)
    )
    test_session.add_all([d1, d2])
    test_session.commit()

    history = dao.get_history_by_user(user_id)

    assert len(history) == 2

    for item in history:
        assert item.ma_nd == user_id


def test_get_history_no_data(test_session, test_app):
    history = dao.get_history_by_user(user_id=888)

    assert len(history) == 0