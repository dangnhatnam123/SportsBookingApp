import math
from datetime import date, time
from app.booking import dao
from app.models import DatLich, San, LoaiSan
from test.test_base import test_session, test_app


def test_get_history_by_user_success(test_session, test_app):
    s = San(ten_san="Sân History",
            active=True,
            loai_san=LoaiSan.BONG_DA)
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


def test_get_history_co_page(test_session, test_app):
    s = San(ten_san="Sân Test Phân Trang", active=True, loai_san=LoaiSan.BONG_DA)
    test_session.add(s)
    test_session.commit()

    user_id = 99
    for i in range(7):
        dl = DatLich(
            ma_nd=user_id,
            ma_san=s.id,
            ngay_choi=date(2026, 5, i + 1),
            gio_bd=time(17, 0),
            gio_kt=time(18, 0)
        )
        test_session.add(dl)
    test_session.commit()

    with test_app.app_context():
        res_list, total_pages = dao.get_history_by_user(user_id, page=1)
        assert isinstance(res_list, list)

        so_don_1_trang = len(res_list)
        assert so_don_1_trang > 0

        expected_pages = math.ceil(7 / so_don_1_trang)

        assert total_pages == expected_pages