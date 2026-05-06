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


def add_user(name, username, password, avatar=None , phone = None):
    password_hashed = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    if NguoiDung.query.filter(NguoiDung.ten_nd == username.strip()).first():
        raise Exception('Tên đăng nhập đã tồn tại!')

    if phone and NguoiDung.query.filter(NguoiDung.so_dien_thoai == phone.strip()).first():
        raise Exception('Số điện thoại này đã được đăng ký!')

    u = NguoiDung(
        ho_ten=name.strip(),
        ten_nd=username.strip(),
        mat_khau=password_hashed,
        so_dien_thoai = phone.strip(),
        vai_tro=VaiTro.NGUOI_DUNG
    )

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get("secure_url")

    db.session.add(u)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Exception('Tên đăng nhập đã tồn tại!')