import random

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Enum, DateTime, Time, Date
from sqlalchemy.orm import relationship
from app import db, app
from flask_login import UserMixin
from enum import Enum as UserEnum
from datetime import datetime, time, date, timedelta
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
    DA_HUY = 3


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
    hinh_anh = Column(String(255), default='https://images.unsplash.com/photo-1518605368461-1e1e38ce71bd?q=80&w=800')

    dat_lichs = relationship('DatLich', backref='san', lazy=True)

    def __str__(self):
        return self.ten_san


class DatLich(BaseModel):
    __tablename__ = 'dat_lich'
    thoi_gian_dat = Column(DateTime, default=datetime.now)
    ngay_choi = Column(Date, nullable=False)
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
        db.drop_all()
        db.create_all()

        pwd = str(hashlib.md5('123456'.encode('utf-8')).hexdigest())
        admin = NguoiDung(ho_ten='Admin Hệ Thống', ten_nd='admin', mat_khau=pwd, vai_tro=VaiTro.QUAN_LY)
        user1 = NguoiDung(ho_ten='Nguyễn Công Phượng', ten_nd='user1', mat_khau=pwd, vai_tro=VaiTro.NGUOI_DUNG)
        user2 = NguoiDung(ho_ten='Lý Hoàng Nam', ten_nd='user2', mat_khau=pwd, vai_tro=VaiTro.NGUOI_DUNG)

        db.session.add_all([admin, user1, user2])
        db.session.commit()


        cum_bong_da = ["Chảo Lửa", "Hoa Lư", "Tao Đàn", "Phú Thọ", "K34", "Thành Phát", "An Khang", "Bách Khoa",
                       "Mỹ Đình", "Thống Nhất"]
        anh_bong_da = "https://images.unsplash.com/photo-1518605368461-1e1e38ce71bd?q=80&w=800"


        cum_cau_long = ["Kỳ Hòa", "Tiến Minh", "Thiên Vân", "Vạn Xuân", "Hải Đăng", "Phượng Hoàng", "Tân Phú", "Gò Vấp",
                        "Bình Minh", "Lan Anh"]
        anh_cau_long = "https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?q=80&w=800"


        cum_tennis = ["Phú Mỹ Hưng", "Thảo Điền", "Đảo Kim Cương", "Sunrise City", "Masteri"]
        anh_tennis = "https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?q=80&w=800"


        s1 = San(ten_san='Sân Bóng Đá A', loai_san=LoaiSan.BONG_DA)
        s2 = San(ten_san='Sân Tennis 1', loai_san=LoaiSan.TENNIS)
        s3 = San(ten_san='Sân Cầu Lông 1', loai_san=LoaiSan.CAU_LONG)

        cac_trang_thai = [TrangThaiSan.CHUA_DAT, TrangThaiSan.DA_DAT, TrangThaiSan.DANG_XU_LY]
        danh_sach_san = []


        for cum in cum_bong_da:
            for i in range(1, 5):
                gia = random.choice([150000, 200000, 250000, 300000])
                tt_ngau_nhien = random.choice(cac_trang_thai)  # Bốc thăm trạng thái
                s = San(
                    ten_san=f"Sân Bóng đá {cum} - Số {i}",
                    loai_san=LoaiSan.BONG_DA,
                    gia_san_theo_gio=gia,
                    hinh_anh=anh_bong_da,
                    trang_thai=tt_ngau_nhien
                )
                danh_sach_san.append(s)


        for cum in cum_cau_long:
            for i in range(1, 5):
                gia = random.choice([60000, 80000, 100000])
                tt_ngau_nhien = random.choice(cac_trang_thai)
                s = San(
                    ten_san=f"CLB Cầu lông {cum} - Sân {i}",
                    loai_san=LoaiSan.CAU_LONG,
                    gia_san_theo_gio=gia,
                    hinh_anh=anh_cau_long,
                    trang_thai=tt_ngau_nhien
                )
                danh_sach_san.append(s)


        for cum in cum_tennis:
            for i in range(1, 5):
                gia = random.choice([200000, 250000, 350000])
                tt_ngau_nhien = random.choice(cac_trang_thai)
                s = San(
                    ten_san=f"Sân Tennis {cum} - VIP {i}",
                    loai_san=LoaiSan.TENNIS,
                    gia_san_theo_gio=gia,
                    hinh_anh=anh_tennis,
                    trang_thai=tt_ngau_nhien
                )
                danh_sach_san.append(s)


        db.session.add_all(danh_sach_san)
        db.session.commit()


        hom_nay = date.today()
        ngay_mai = hom_nay + timedelta(days=1)
        san_bd_1 = danh_sach_san[0]
        san_cl_1 = danh_sach_san[40]

        lich_mau = [
            DatLich(ngay_choi=hom_nay, gio_bd=time(18, 0), gio_kt=time(19, 0), ma_nd=user1.id, ma_san=san_bd_1.id,
                    trang_thai=TrangThaiDL.DA_HOAN_THANH),
            DatLich(ngay_choi=ngay_mai, gio_bd=time(17, 0), gio_kt=time(18, 0), ma_nd=user2.id, ma_san=san_bd_1.id,
                    trang_thai=TrangThaiDL.CHUA_HOAN_THANH),
            DatLich(ngay_choi=ngay_mai, gio_bd=time(18, 0), gio_kt=time(19, 0), ma_nd=user1.id, ma_san=san_cl_1.id,
                    trang_thai=TrangThaiDL.CHUA_HOAN_THANH),
        ]

        db.session.add_all(lich_mau)
        db.session.commit()

        print("Khởi tạo Database và dữ liệu mẫu thành công!")