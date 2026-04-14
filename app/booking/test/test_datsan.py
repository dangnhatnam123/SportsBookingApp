import hashlib
import pytest
from app.models import NguoiDung, San


@pytest.fixture()
def setup_booking_data(test_session):
    pw = str(hashlib.md5('123456'.encode('utf-8')).hexdigest())

    u = NguoiDung(ho_ten="Khach Dat San", ten_nd="khach_vip", mat_khau=pw, vai_tro=VaiTro.NGUOI_DUNG)

    s1 = San(ten_san="Sân Chảo Lửa 1", loai_san="Bóng đá", gia_san_theo_gio=100000, active=True)
    s2 = San(ten_san="Sân Chảo Lửa 2", loai_san="Bóng đá", gia_san_theo_gio=100000, active=True)

    test_session.add_all([u, s1, s2])
    test_session.commit()

    return {'user': u, 'san1': s1, 'san2': s2}

