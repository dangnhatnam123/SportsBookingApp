from app import db
from app.models import DatLich, TrangThaiDL, San, HoaDon


def get_ds_lich_trong_ngay(ngay_chon):
    return DatLich.query.filter(DatLich.ngay_choi == ngay_chon).order_by(DatLich.gio_bd.asc()).all()


def xac_nhan_nhan_san(booking_id):
    try:
        lich = DatLich.query.get(booking_id)
        if lich:
            lich.trang_thai = TrangThaiDL.DA_HOAN_THANH
            db.session.commit()
            return lich
        return None
    except Exception as ex:
        print(f"Lỗi xác nhận nhận sân: {str(ex)}")
        db.session.rollback()
        return None

def get_all_san():
    return San.query.all()

def get_lich_su_giao_dich(ma_nv):
    return HoaDon.query.filter(HoaDon.ma_nv == ma_nv).order_by(HoaDon.ngay_tao.desc()).all()