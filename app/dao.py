from app.models import NguoiDung, San, DatLich, TrangThaiDL
from app import db
from datetime import datetime, timedelta
import hashlib

def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return NguoiDung.query.filter(NguoiDung.ten_nd == username,
                                  NguoiDung.mat_khau == password).first()

def dat_san(user_id, san_id, ngay, gio_bd, gio_kt):
    # Ràng buộc: Một người chỉ được đặt tối đa 3 sân/ngày
    count = DatLich.query.filter(DatLich.ma_nd == user_id,
                                 DatLich.ngay_dat == ngay).count()
    if count >= 3:
        return False, "Bạn đã đạt giới hạn 3 sân/ngày!"

    # Ràng buộc: Khung giờ đặt tối thiểu 1 giờ
    start = datetime.combine(datetime.today(), gio_bd)
    end = datetime.combine(datetime.today(), gio_kt)
    if (end - start).total_seconds() < 3600:
        return False, "Thời gian đặt tối thiểu phải là 1 giờ!"

    new_booking = DatLich(ma_nd=user_id, ma_san=san_id, ngay_dat=ngay,
                         gio_bd=gio_bd, gio_kt=gio_kt)
    db.session.add(new_booking)
    db.session.commit()
    return True, "Đặt sân thành công!"