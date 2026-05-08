import hashlib
from datetime import datetime, timedelta, time
import pytest
from flask import Flask
from app import db, login_manager
from app.auth.views import auth_bp
from app.booking.views import booking_bp
from app.courts.views import courts_bp
from app.models import NguoiDung, San, LoaiSan, VaiTro, DatLich


def create_app():
    app = Flask(__name__, template_folder='../app/templates', static_folder='../app/static')
    app.config.update({
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "PAGE_SIZE": 2,
        "TESTING": True,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": '34y394yjsbdkjsdjksdh'
    })

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(courts_bp)

    return app


@pytest.fixture(scope='session')
def test_app():
    app = create_app()
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def test_client(test_app):
    return test_app.test_client()


@pytest.fixture
def test_session(test_app):
    with test_app.app_context():
        db.session.remove()
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
        yield db.session
        db.session.rollback()
        db.session.remove()


@pytest.fixture
def mock_cloudinary(monkeypatch):
    def fake_upload(file, **kwargs):
        return {'secure_url': 'https://fake-avatar.png'}

    monkeypatch.setattr('cloudinary.uploader.upload', fake_upload)

@pytest.fixture()
def setup_booking_data(test_session):
    pw = str(hashlib.md5('123456'.encode('utf-8')).hexdigest())

    user = NguoiDung(ho_ten="Lê Văn Sĩ", ten_nd="khach", mat_khau=pw,
                  email="khach@gmail.com", so_dien_thoai="0123456789",
                  vai_tro=VaiTro.NGUOI_DUNG)

    admin = NguoiDung(ho_ten="Quản Lý Hệ Thống", ten_nd="admin", mat_khau=pw,
                      email="admin@gmail.com", so_dien_thoai="0999999999", vai_tro=VaiTro.QUAN_LY)

    s1 = San(ten_san="Sân Chảo Lửa 1", loai_san=LoaiSan.BONG_DA, gia_san_theo_gio=100000, active=True)
    s2 = San(ten_san="Sân Chảo Lửa 2", loai_san=LoaiSan.BONG_DA, gia_san_theo_gio=100000, active=True)

    test_session.add_all([user,admin, s1, s2])
    test_session.commit()

    ngay_mai = (datetime.now() + timedelta(days=1)).date()
    dat_lich = DatLich(ma_nd=user.id, ma_san=s1.id, ngay_choi=ngay_mai,
                       gio_bd=time(10, 0), gio_kt=time(11, 0))
    test_session.add(dat_lich)
    test_session.commit()

    return {'user': user, 'admin': admin, 'san1': s1, 'san2': s2}

