import hashlib
from app.models import NguoiDung, VaiTro
from app import db
from sqlalchemy.exc import IntegrityError


# Lấy người dùng theo ID (Dùng cho Flask-Login)
def get_user_by_id(user_id):
    return NguoiDung.query.get(user_id)


# Kiểm tra đăng nhập
def auth_user(username, password):
    # Băm MD5 theo chuẩn file models.py của bạn
    password_hashed = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    return NguoiDung.query.filter(NguoiDung.ten_nd == username.strip(),
                                  NguoiDung.mat_khau == password_hashed).first()


# Thêm người dùng mới (Đăng ký)
def add_user(name, username, password):
    # Băm MD5
    password_hashed = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    # Tạo user mới, ghép đúng các trường: ho_ten, ten_nd, mat_khau
    u = NguoiDung(
        ho_ten=name.strip(),
        ten_nd=username.strip(),
        mat_khau=password_hashed,
        vai_tro=VaiTro.NGUOI_DUNG  # Mặc định là NGUOI_DUNG
    )

    db.session.add(u)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Exception('Tên đăng nhập đã tồn tại!')