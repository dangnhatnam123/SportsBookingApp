import hashlib
import cloudinary.uploader
from sqlalchemy.exc import IntegrityError
from app.extention import db
from app.models import NguoiDung, VaiTro


def get_user_by_id(user_id):
    return NguoiDung.query.get(user_id)


def auth_user(username, password):
    password_hashed = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    return NguoiDung.query.filter(NguoiDung.ten_nd == username.strip(),
                                  NguoiDung.mat_khau == password_hashed,
                                  NguoiDung.active == True).first()

def check_existing_user(username, phone, email):
    return NguoiDung.query.filter(
        (NguoiDung.ten_nd == username.strip()) |
        (NguoiDung.so_dien_thoai == phone.strip()) |
        (NguoiDung.email == email.strip())
    ).first() is not None

def add_user(name, username, password,  phone, email,avatar=None):
    if NguoiDung.query.filter(NguoiDung.ten_nd == username.strip()).first():
        raise Exception('Tên đăng nhập đã tồn tại!')

    if phone and NguoiDung.query.filter(NguoiDung.so_dien_thoai == phone.strip()).first():
        raise Exception('Số điện thoại này đã được đăng ký!')

    if email and NguoiDung.query.filter(NguoiDung.email == email.strip()).first():
        raise Exception('Email này đã được đăng ký!')

    password_hashed = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = NguoiDung(
        ho_ten=name.strip(),
        ten_nd=username.strip(),
        email=email.strip(),
        mat_khau=password_hashed,
        so_dien_thoai=phone.strip(),
        vai_tro=VaiTro.NGUOI_DUNG
    )

    if avatar and avatar.filename:
        try:
            res = cloudinary.uploader.upload(avatar)
            u.avatar = res.get("secure_url")
        except Exception:
            raise Exception('Lỗi khi tải ảnh đại diện lên máy chủ!')

    db.session.add(u)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Exception('Lỗi hệ thống, không thể lưu dữ liệu!')
