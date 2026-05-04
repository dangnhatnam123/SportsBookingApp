from datetime import datetime

from app.extention import db
from app.models import San, DatLich, HoaDon


def load_all_san():
    return San.query.all()

def add_san_moi(ten, loai, gia_thue):
    san_moi = San(ten_san=ten, loai_san=loai, gia_san_theo_gio=gia_thue)
    db.session.add(san_moi)
    db.session.commit()

def kiem_tra_lich_dat(san_id):
    return DatLich.query.filter(
    DatLich.ma_san == san_id,
        DatLich.ngay_choi >= datetime.now().date()
    ).first() is not None

def xoa_san(san_id):
    san = San.query.get(san_id)
    if san:
        db.session.delete(san)
        db.session.commit()

def get_san(san_id):
    return San.query.get(san_id)

def update_san(san_id, ten, loai, gia_san_theo_gio):
    san = San.query.get(san_id)
    if san:
        san.ten_san = ten
        san.loai_san = loai
        san.gia_san_theo_gio = gia_san_theo_gio
        db.session.commit()

def check_ten_san(ten, exclude_id = None):
    query = San.query.filter(San.ten_san == ten)
    if exclude_id:
        query = query.filter(San.id != exclude_id)
    return query.first() is not None

