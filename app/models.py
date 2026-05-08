import random
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Enum, DateTime, Time, Date
from sqlalchemy.orm import relationship

from app.extention import db

from flask_login import UserMixin
from enum import Enum as UserEnum
from datetime import datetime, time, date, timedelta
import hashlib

class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean, default=True)


class VaiTro(UserEnum):
    NGUOI_DUNG = "Người Dùng"
    NHAN_VIEN = "Nhân Viên"
    QUAN_LY = "Quản Lý"


class GioiTinh(UserEnum):
    NAM = "Nam"
    NU = "Nữ"
    KHAC = "Khác"


class LoaiSan(UserEnum):
    BONG_DA = "Bóng Đá"
    TENNIS = "Tennis"
    CAU_LONG = "Cầu Lông"


class TrangThaiDL(UserEnum):
    DA_HOAN_THANH = "Đã Hoàn Thành"
    CHUA_HOAN_THANH = "Chưa Hoàn Thành"
    DA_HUY = "Đã Hủy"


class TrangThaiHoaDon(UserEnum):
    DA_THANH_TOAN = "Đã Thanh Toán"
    CHUA_THANH_TOAN = "Chưa Thanh Toán"
    DA_HUY = "Đã Hủy"


class NguoiDung(BaseModel, UserMixin):
    __tablename__ = 'nguoi_dung'
    ho_ten = Column(String(100), nullable=False)
    ten_nd = Column(String(50), nullable=False, unique=True)
    mat_khau = Column(String(100), nullable=False)
    vai_tro = Column(Enum(VaiTro), default=VaiTro.NGUOI_DUNG)
    gioi_tinh = Column(Enum(GioiTinh))
    so_dien_thoai = Column(String(15), nullable=True, unique=True)
    email = Column(String(100), unique=True, nullable=False)
    avatar = Column(String(255),
                    default='https://cdn-icons-png.flaticon.com/512/149/149071.png')
    ngay_vao_lam = Column(DateTime)
    ma_ql = Column(String(20))

    dat_lichs = relationship('DatLich', back_populates='nguoi_dung', lazy=True)
    hoa_dons = relationship('HoaDon', back_populates='nhan_vien', lazy=True)

    def __str__(self):
        return self.ho_ten # pragma: no cover


class San(BaseModel):
    __tablename__ = 'san'
    ten_san = Column(String(50), nullable=False, unique=True)
    loai_san = Column(Enum(LoaiSan), nullable=False)
    gia_san_theo_gio = Column(Float, default=100000)
    hinh_anh = Column(String(255), default='https://images.unsplash.com/photo-1518605368461-1e1e38ce71bd?q=80&w=800')

    dat_lichs = relationship('DatLich', back_populates='san', lazy=True)

    def __str__(self):
        return self.ten_san # pragma: no cover



class DatLich(BaseModel):
    __tablename__ = 'dat_lich'
    thoi_gian_dat = Column(DateTime, default=datetime.now)
    ngay_choi = Column(Date, nullable=False)
    gio_bd = Column(Time, nullable=False)
    gio_kt = Column(Time, nullable=False)
    trang_thai = Column(Enum(TrangThaiDL), default=TrangThaiDL.CHUA_HOAN_THANH)

    loai_thanh_toan = Column(String(20), default='truc_tiep')
    momo_trans_id = Column(String(100), nullable=True)

    ma_nd = Column(Integer, ForeignKey('nguoi_dung.id'), nullable=False)
    ma_san = Column(Integer, ForeignKey('san.id'), nullable=False)

    nguoi_dung = relationship('NguoiDung', back_populates='dat_lichs')
    san = relationship('San', back_populates='dat_lichs')
    hoa_don = relationship('HoaDon', back_populates='dat_lich', uselist=False)

    # @property
    # def trang_thai_hien_tai(self):
    #     if self.trang_thai == TrangThaiDL.DA_HUY:
    #         return "Đã hủy"
    #     now = datetime.now()
    #     start_dt = datetime.combine(self.ngay_choi, self.gio_bd)
    #     end_dt = datetime.combine(self.ngay_choi, self.gio_kt)
    #     if now < start_dt:
    #         return "Chờ nhận sân"
    #
    #     if self.trang_thai == TrangThaiDL.DA_HOAN_THANH:
    #         if now > end_dt:
    #             return "Hết giờ chơi"
    #
    #         return "Sân đang được sử dụng"
    #
    #     if now > end_dt:
    #         return "Hết giờ nhận sân"
    #     return "Chờ nhận sân"

class HoaDon(BaseModel):
    __tablename__ = 'hoa_don'
    tong_tien = Column(Float, default=0)
    ngay_tao = Column(DateTime, default=datetime.now())
    trang_thai = Column(Enum(TrangThaiHoaDon), default=TrangThaiHoaDon.CHUA_THANH_TOAN)

    ma_dat = Column(Integer, ForeignKey('dat_lich.id'), nullable=False)
    ma_nv = Column(Integer, ForeignKey('nguoi_dung.id'))

    dat_lich = relationship('DatLich', back_populates='hoa_don')
    nhan_vien = relationship('NguoiDung', back_populates='hoa_dons')