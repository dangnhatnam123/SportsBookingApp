from datetime import datetime, timedelta
from sqlalchemy import func
from app.extention import db
from app.models import DatLich, TrangThaiDL, TrangThaiHoaDon, HoaDon, San
from flask import current_app


def load_san_trong(loai_san_val=None, ngay=None, gio_bd=None, gio_kt=None, page=1):
    query = San.query.filter(San.active == True)
    if loai_san_val:
        query = query.filter(San.loai_san == loai_san_val)

    if ngay and gio_bd and gio_kt:
        da_dat = db.session.query(DatLich.ma_san).filter(
            DatLich.ngay_choi == ngay,
            DatLich.trang_thai != TrangThaiDL.DA_HUY,  # Chỉ tính sân chưa hủy
            (DatLich.gio_bd < gio_kt) & (DatLich.gio_kt > gio_bd)
        )
        query = query.filter(~San.id.in_(da_dat))

    page_size = current_app.config.get('PAGE_SIZE', 6)
    start = (page - 1) * page_size
    return query.slice(start, start + page_size).all()


def count_san_trong(loai_san_val=None, ngay=None, gio_bd=None, gio_kt=None):
    query = San.query.filter(San.active == True)
    if loai_san_val: query = query.filter(San.loai_san == loai_san_val)
    if ngay and gio_bd and gio_kt:
        da_dat = db.session.query(DatLich.ma_san).filter(
            DatLich.ngay_choi == ngay,
            DatLich.trang_thai != TrangThaiDL.DA_HUY,
            (DatLich.gio_bd < gio_kt) & (DatLich.gio_kt > gio_bd)
        )
        query = query.filter(~San.id.in_(da_dat))
    return query.count()


def count_san_by_type():
    return db.session.query(San.loai_san, func.count(San.id)).group_by(San.loai_san).all()


def get_san_by_id(san_id):
    return San.query.get(san_id)


def luu_dat_san(ma_nd, ma_san, ngay_choi, gio_bd, gio_kt, tong_tien, loai_thanh_toan='truc_tiep'):
    try:
        ngay_obj = datetime.strptime(ngay_choi, '%Y-%m-%d').date()
        gio_bd_obj = datetime.strptime(gio_bd, '%H:%M').time()
        gio_kt_obj = datetime.strptime(gio_kt, '%H:%M').time()

        gia_lap_momo_id = None
        if loai_thanh_toan == 'momo':
            gia_lap_momo_id = f"MOMO_TEST_{int(datetime.now().timestamp())}"

        dat_lich = DatLich(
            ngay_choi=ngay_obj,
            gio_bd=gio_bd_obj,
            gio_kt=gio_kt_obj,
            ma_nd=ma_nd,
            ma_san=ma_san,
            trang_thai=TrangThaiDL.CHUA_HOAN_THANH,
            loai_thanh_toan=loai_thanh_toan
        )
        db.session.add(dat_lich)
        db.session.flush()

        trang_thai_hd = TrangThaiHoaDon.CHUA_THANH_TOAN
        if loai_thanh_toan == 'truc_tiep':
            trang_thai_hd = TrangThaiHoaDon.DA_THANH_TOAN

        hoa_don = HoaDon(
            tong_tien=float(tong_tien),
            ngay_tao=datetime.now(),
            trang_thai=trang_thai_hd,
            ma_dat=dat_lich.id,
        )
        db.session.add(hoa_don)
        db.session.commit()
        return dat_lich
    except Exception as ex:
        print(f"Lỗi khi lưu DB: {str(ex)}")
        db.session.rollback()
        return False

def cap_nhat_thanh_toan_thanh_cong(ma_dat_san, trans_id=None):
    try:
        dat_lich = DatLich.query.get(ma_dat_san)
        if dat_lich:
            if trans_id:
                dat_lich.momo_trans_id = trans_id

            if dat_lich.hoa_don:
                dat_lich.hoa_don.trang_thai = TrangThaiHoaDon.DA_THANH_TOAN

            db.session.commit()
            return True
    except Exception as ex:
        print(f"Lỗi cập nhật thanh toán: {ex}")
        db.session.rollback()
    return False


def get_history_by_user(user_id, page=None):
    query = DatLich.query.filter(DatLich.ma_nd == user_id).order_by(DatLich.thoi_gian_dat.desc())
    if page:
        page_size = current_app.config.get('PAGE_SIZE', 6)
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        return pagination.items, pagination.pages
    return query.all()

def update_momo_trans_id(ma_dat_san, trans_id):
    dat_lich = DatLich.query.get(ma_dat_san)
    if dat_lich:
        dat_lich.momo_trans_id = trans_id
        db.session.commit()
        return True
    return False

def huy_dat_san(ma_dat_san):
    try:
        dat_lich = DatLich.query.get(ma_dat_san)
        if not dat_lich:
            return False

        dat_lich.trang_thai = TrangThaiDL.DA_HUY
        if dat_lich.hoa_don:
            dat_lich.hoa_don.trang_thai = TrangThaiHoaDon.DA_HUY

        db.session.commit()
        return True
    except Exception as ex:
        print(f"Lỗi khi hủy trên DB: {ex}")
        db.session.rollback()
        return False


def count_dat_san_trong_ngay(ma_nd, ngay_choi):
    ngay = datetime.strptime(ngay_choi, '%Y-%m-%d').date()
    return DatLich.query.filter(
        DatLich.ma_nd == ma_nd,
        DatLich.ngay_choi == ngay,
        DatLich.trang_thai != TrangThaiDL.DA_HUY
    ).count()

def xoa_don_loi(ma_dat_san):
    don_hang = DatLich.query.get(ma_dat_san)
    if don_hang:
        if don_hang.hoa_don:
            db.session.delete(don_hang.hoa_don)
        db.session.delete(don_hang)
        db.session.commit()
        return True
    return False