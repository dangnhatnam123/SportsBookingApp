import hashlib
from datetime import datetime, timedelta, time
import pytest
from flask import Flask
from app import db, login_manager
from app.auth.views import auth_bp
from app.booking.views import booking_bp
from app.courts.views import courts_bp
from app.models import NguoiDung, San, LoaiSan, VaiTro, DatLich
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


# 1. Hàm tạo App để Test
def create_app():
    app = Flask(__name__, template_folder='../app/templates', static_folder='../app/static')
    app.config.update({
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "TESTING": True,
        "SECRET_KEY": '34y394yjsbdkjsdjksdh'
    })
    db.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(courts_bp)
    return app


# 2. Fixture khởi tạo App
@pytest.fixture(scope='session')
def test_app():
    app = create_app()
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


# --- ĐÂY LÀ PHẦN BẠN CẦN BỔ SUNG/SỬA ---
@pytest.fixture
def test_session(test_app):
    """Fixture này cung cấp session để làm việc với Database ảo"""
    with test_app.app_context():
        yield db.session
        db.session.rollback()  # Xóa dữ liệu sau mỗi lần test để không bị lẫn lộn


# 3. Sửa hàm setup_booking_data (Không để pass nữa)
@pytest.fixture()
def setup_booking_data(test_session):
    # Mã hóa mật khẩu MD5 đúng chuẩn đồ án của bạn
    pw = str(hashlib.md5('123456'.encode('utf-8')).hexdigest())

    # Tạo tài khoản Admin mẫu
    admin = NguoiDung(ho_ten="Admin Hệ Thống", ten_nd="admin", mat_khau=pw,
                      vai_tro=VaiTro.QUAN_LY, email="admin@gmail.com")

    # Tạo sân mẫu với giá 100,000đ/giờ (để Selenium dễ tính toán)
    s1 = San(ten_san="Sân Chảo Lửa 1", gia_san_theo_gio=100000, active=True)

    test_session.add_all([admin, s1])
    test_session.commit()

    return {'admin': admin, 'san1': s1}


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    yield driver
    driver.quit()