# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary

# 1. Khởi tạo các công cụ (chưa gắn vào app)
db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    # 2. Cấu hình cơ bản
    app.secret_key = 'aaaaaaaaaa'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3307/sportdb?charset=utf8mb4'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["PAGE_SIZE"] = 6

    # 3. Cấu hình Cloudinary
    cloudinary.config(
        cloud_name='dxxwcby8l',
        api_key='792844686918347',
        api_secret='T8ys_Z9zaKSqmKWa4K1RY6DXUJg'
    )

    # 4. Gắn công cụ vào app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_bp.login_view'  # Khi chưa đăng nhập sẽ đá về đây

    # 5. Đăng ký các Module (Blueprints)
    from app.auth.views import auth_bp
    from app.courts.views import courts_bp
    from app.booking.views import booking_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(courts_bp)
    app.register_blueprint(booking_bp)

    return app