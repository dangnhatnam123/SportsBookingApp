import hashlib
from app.models import NguoiDung, VaiTro
from app import db
from sqlalchemy.exc import IntegrityError


def get_user_by_id(user_id):
    return NguoiDung.query.get(user_id)


def auth_user(username, password):

    password_hashed = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    return NguoiDung.query.filter(NguoiDung.ten_nd == username.strip(),
                                  NguoiDung.mat_khau == password_hashed).first()


def add_user(name, username, password):

    password_hashed = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    u = NguoiDung(
        ho_ten=name.strip(),
        ten_nd=username.strip(),
        mat_khau=password_hashed,
        vai_tro=VaiTro.NGUOI_DUNG
    )

    db.session.add(u)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Exception('Tên đăng nhập đã tồn tại!')