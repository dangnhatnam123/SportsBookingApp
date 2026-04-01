import hashlib
from datetime import datetime

from sqlalchemy import func

from app import db, app
from sqlalchemy.exc import IntegrityError
from app.models import NguoiDung, VaiTro, San, DatLich, TrangThaiDL, TrangThaiHoaDon, HoaDon
import cloudinary.uploader


def get_user_by_id(user_id):
    return NguoiDung.query.get(user_id)


def auth_user(username, password):
    password_hashed = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    return NguoiDung.query.filter(NguoiDung.ten_nd == username.strip(),
                                  NguoiDung.mat_khau == password_hashed).first()


def add_user(name, username, password, avatar=None):
    password_hashed = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    u = NguoiDung(
        ho_ten=name.strip(),
        ten_nd=username.strip(),
        mat_khau=password_hashed,
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


def load_san_trong(kw=None, loai_san_val=None, ngay=None, gio_bd=None, gio_kt=None, page=1):
    query = San.query.filter(San.active == True)

    if kw:
        query = query.filter(San.ten_san.contains(kw))
    if loai_san_val:
        query = query.filter(San.loai_san == loai_san_val)

    if ngay and gio_bd and gio_kt:
        da_dat = db.session.query(DatLich.ma_san).filter(
            DatLich.ngay_choi == ngay,
            (DatLich.gio_bd < gio_kt) & (DatLich.gio_kt > gio_bd)
        )
        query = query.filter(~San.id.in_(da_dat))

    page_size = app.config.get('PAGE_SIZE', 9)
    start = (page - 1) * page_size
    return query.slice(start, start + page_size).all()


def count_san_trong(kw=None, loai_san_val=None, ngay=None, gio_bd=None, gio_kt=None):
    query = San.query.filter(San.active == True)
    if kw: query = query.filter(San.ten_san.contains(kw))
    if loai_san_val: query = query.filter(San.loai_san == loai_san_val)
    if ngay and gio_bd and gio_kt:
        da_dat = db.session.query(DatLich.ma_san).filter(DatLich.ngay_choi == ngay,
                                                         (DatLich.gio_bd < gio_kt) & (DatLich.gio_kt > gio_bd))
        query = query.filter(~San.id.in_(da_dat))
    return query.count()


def count_san_by_type():
    return db.session.query(San.loai_san, func.count(San.id)).group_by(San.loai_san).all()


def get_san_by_id(san_id):
    return San.query.get(san_id)


def luu_dat_san(ma_nd, ma_san, ngay_choi, gio_bd, gio_kt, tong_tien):
    try:
        ngay_obj = datetime.strptime(ngay_choi, '%Y-%m-%d').date()
        gio_bd_obj = datetime.strptime(gio_bd, '%H:%M').time()
        gio_kt_obj = datetime.strptime(gio_kt, '%H:%M').time()

        dat_lich = DatLich(
            ngay_choi=ngay_obj,
            gio_bd=gio_bd_obj,
            gio_kt=gio_kt_obj,
            ma_nd=ma_nd,
            ma_san=ma_san,
            trang_thai=TrangThaiDL.CHUA_HOAN_THANH
        )
        db.session.add(dat_lich)
        db.session.flush()  # Đẩy tạm vào DB để lấy được dat_lich.id (mã đặt)

        hoa_don = HoaDon(
            tong_tien=float(tong_tien),
            ngay_tao=datetime.now(),
            trang_thai=TrangThaiHoaDon.DA_THANH_TOAN,
            ma_dat=dat_lich.id
        )
        db.session.add(hoa_don)

        db.session.commit()
        return True

    except Exception as ex:
        print(f"Lỗi khi lưu DB: {str(ex)}")
        db.session.rollback()
        return False