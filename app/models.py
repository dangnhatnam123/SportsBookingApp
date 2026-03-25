from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Enum, DateTime, Time
from sqlalchemy.orm import relationship
from app import db, app
from flask_login import UserMixin
from enum import Enum as UserEnum
from datetime import datetime, time
import hashlib


class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean, default=True)


class VaiTro(UserEnum):
    NGUOI_DUNG = 1
    NHAN_VIEN = 2
    QUAN_LY = 3


class GioiTinh(UserEnum):
    NAM = 1
    NU = 2
    KHAC = 3


class LoaiSan(UserEnum):
    BONG_DA = 1
    TENNIS = 2
    CAU_LONG = 3


class TrangThaiSan(UserEnum):
    DA_DAT = 1
    CHUA_DAT = 2
    DANG_XU_LY = 3


class TrangThaiDL(UserEnum):
    DA_HOAN_THANH = 1
    CHUA_HOAN_THANH = 2


class TrangThaiHoaDon(UserEnum):
    DA_THANH_TOAN = 1
    CHUA_THANH_TOAN = 2


class NguoiDung(BaseModel, UserMixin):
    __tablename__ = 'nguoi_dung'
    ho_ten = Column(String(100), nullable=False)
    ten_nd = Column(String(50), nullable=False, unique=True)
    mat_khau = Column(String(100), nullable=False)
    vai_tro = Column(Enum(VaiTro), default=VaiTro.NGUOI_DUNG)
    gioi_tinh = Column(Enum(GioiTinh))

    ngay_vao_lam = Column(DateTime)
    ma_ql = Column(String(20))

    dat_lichs = relationship('DatLich', backref='nguoi_dung', lazy=True)
    hoa_dons = relationship('HoaDon', backref='nhan_vien', lazy=True)

    def __str__(self):
        return self.ho_ten


class San(BaseModel):
    __tablename__ = 'san'
    ten_san = Column(String(50), nullable=False, unique=True)
    loai_san = Column(Enum(LoaiSan), nullable=False)
    trang_thai = Column(Enum(TrangThaiSan), default=TrangThaiSan.CHUA_DAT)
    gia_san_theo_gio = Column(Float, default=100000)

    dat_lichs = relationship('DatLich', backref='san', lazy=True)

    def __str__(self):
        return self.ten_san


class DatLich(BaseModel):
    __tablename__ = 'dat_lich'
    ngay_dat = Column(DateTime, default=datetime.now)
    gio_bd = Column(Time, nullable=False)
    gio_kt = Column(Time, nullable=False)
    trang_thai = Column(Enum(TrangThaiDL), default=TrangThaiDL.CHUA_HOAN_THANH)

    ma_nd = Column(Integer, ForeignKey(NguoiDung.id), nullable=False)
    ma_san = Column(Integer, ForeignKey(San.id), nullable=False)

    hoa_don = relationship('HoaDon', backref='dat_lich', uselist=False)


class HoaDon(BaseModel):
    __tablename__ = 'hoa_don'
    tong_tien = Column(Float, default=0)
    ngay_tao = Column(DateTime, default=datetime.now())
    trang_thai = Column(Enum(TrangThaiHoaDon), default=TrangThaiHoaDon.CHUA_THANH_TOAN)

    ma_dat = Column(Integer, ForeignKey(DatLich.id), nullable=False)
    ma_nv = Column(Integer, ForeignKey(NguoiDung.id))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()


        pwd = str(hashlib.md5('123456'.encode('utf-8')).hexdigest())
        u1 = NguoiDung(ho_ten='Quan Ly Sân', ten_nd='admin', mat_khau=pwd, vai_tro=VaiTro.QUAN_LY)
        u2 = NguoiDung(ho_ten='Nguyễn Văn A', ten_nd='user1', mat_khau=pwd, vai_tro=VaiTro.NGUOI_DUNG)

        db.session.add_all([u1, u2])
        db.session.commit()


        s1 = San(ten_san='Sân Bóng Đá A', loai_san=LoaiSan.BONG_DA)
        s2 = San(ten_san='Sân Tennis 1', loai_san=LoaiSan.TENNIS)
        s3 = San(ten_san='Sân Cầu Lông 1', loai_san=LoaiSan.CAU_LONG)

        db.session.add_all([s1, s2, s3])
        db.session.commit()


        dl1 = DatLich(ngay_dat=datetime.now(),
                      gio_bd=time(8, 0),
                      gio_kt=time(9, 0),
                      ma_nd=u2.id,
                      ma_san=s1.id)

        db.session.add(dl1)
        db.session.commit()

        print("Khởi tạo Database và dữ liệu mẫu thành công!")