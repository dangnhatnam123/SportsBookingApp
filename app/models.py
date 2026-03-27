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


class TrangThaiSan(UserEnum):
    DA_DAT = "Đã Đặt"
    CHUA_DAT = "Chưa Đặt"
    DANG_XU_LY = "Đang Xử Lý"


class TrangThaiDL(UserEnum):
    DA_HOAN_THANH = "Đã Hoàn Thành"
    CHUA_HOAN_THANH = "Chưa Hoàn Thành"
    DA_HUY = "Đã Hủy"


class TrangThaiHoaDon(UserEnum):
    DA_THANH_TOAN = "Đã Thanh Toán"
    CHUA_THANH_TOAN = "Chưa Thanh Toán"


class NguoiDung(BaseModel, UserMixin):
    __tablename__ = 'nguoi_dung'
    __table_args__ = {'extend_existing': True}

    ho_ten = Column(String(100), nullable=False)
    ten_nd = Column(String(50), nullable=False, unique=True)
    mat_khau = Column(String(100), nullable=False)
    vai_tro = Column(Enum(VaiTro), default=VaiTro.NGUOI_DUNG)
    gioi_tinh = Column(Enum(GioiTinh))
    avatar = Column(String(255),
                    default='https://cdn-icons-png.flaticon.com/512/149/149071.png')
    ngay_vao_lam = Column(DateTime)
    ma_ql = Column(String(20))

    dat_lichs = relationship('DatLich', back_populates='nguoi_dung', lazy=True)
    hoa_dons = relationship('HoaDon', back_populates='nhan_vien', lazy=True)

    def __str__(self):
        return self.ho_ten


class San(BaseModel):
    __tablename__ = 'san'
    __table_args__ = {'extend_existing': True}

    ten_san = Column(String(50), nullable=False, unique=True)
    loai_san = Column(Enum(LoaiSan), nullable=False)
    trang_thai = Column(Enum(TrangThaiSan), default=TrangThaiSan.CHUA_DAT)
    gia_san_theo_gio = Column(Float, default=100000)
    hinh_anh = Column(String(255), default='https://images.unsplash.com/photo-1518605368461-1e1e38ce71bd?q=80&w=800')

    dat_lichs = relationship('DatLich', back_populates='san', lazy=True)

    def __str__(self):
        return self.ten_san


class DatLich(BaseModel):
    __tablename__ = 'dat_lich'
    __table_args__ = {'extend_existing': True}

    thoi_gian_dat = Column(DateTime, default=datetime.now)
    ngay_choi = Column(Date, nullable=False)
    gio_bd = Column(Time, nullable=False)
    gio_kt = Column(Time, nullable=False)
    trang_thai = Column(Enum(TrangThaiDL), default=TrangThaiDL.CHUA_HOAN_THANH)

    ma_nd = Column(Integer, ForeignKey('nguoi_dung.id'), nullable=False)
    ma_san = Column(Integer, ForeignKey('san.id'), nullable=False)

    nguoi_dung = relationship('NguoiDung', back_populates='dat_lichs')
    san = relationship('San', back_populates='dat_lichs')
    hoa_don = relationship('HoaDon', back_populates='dat_lich', uselist=False)


class HoaDon(BaseModel):
    __tablename__ = 'hoa_don'
    __table_args__ = {'extend_existing': True}

    tong_tien = Column(Float, default=0)
    ngay_tao = Column(DateTime, default=datetime.now())
    trang_thai = Column(Enum(TrangThaiHoaDon), default=TrangThaiHoaDon.CHUA_THANH_TOAN)

    ma_dat = Column(Integer, ForeignKey('dat_lich.id'), nullable=False)
    ma_nv = Column(Integer, ForeignKey('nguoi_dung.id'))

    dat_lich = relationship('DatLich', back_populates='hoa_don')
    nhan_vien = relationship('NguoiDung', back_populates='hoa_dons')


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

        data_set = [
            {
                "cums": ["Chảo Lửa", "Hoa Lư", "Tao Đàn", "Phú Thọ", "K34", "Thành Phát", "An Khang", "Bách Khoa",
                         "Mỹ Đình", "Thống Nhất"],
                "loai": LoaiSan.BONG_DA,
                "anh": "https://images.unsplash.com/photo-1518605368461-1e1e38ce71bd?q=80&w=800",
                "gia_list": [150000, 200000, 250000, 300000],
                "prefix": "Sân Bóng đá"
            },
            {
                "cums": ["Kỳ Hòa", "Tiến Minh", "Thiên Vân", "Vạn Xuân", "Hải Đăng", "Phượng Hoàng", "Tân Phú",
                         "Gò Vấp", "Bình Minh", "Lan Anh"],
                "loai": LoaiSan.CAU_LONG,
                "anh": "https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?q=80&w=800",
                "gia_list": [60000, 80000, 100000],
                "prefix": "CLB Cầu lông"
            },
            {
                "cums": ["Phú Mỹ Hưng", "Thảo Điền", "Đảo Kim Cương", "Sunrise City", "Masteri"],
                "loai": LoaiSan.TENNIS,
                "anh": "https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?q=80&w=800",
                "gia_list": [200000, 250000, 350000],
                "prefix": "Sân Tennis"
            }
        ]

        cac_trang_thai_san = [TrangThaiSan.CHUA_DAT, TrangThaiSan.DA_DAT, TrangThaiSan.DANG_XU_LY]

        danh_sach_san = []
        for item in data_set:
            for cum in item["cums"]:
                for i in range(1, 5):
                    # Lấy trạng thái ngẫu nhiên cho từng cái sân
                    tt_ngau_nhien = random.choice(cac_trang_thai_san)

                    s = San(
                        ten_san=f"{item['prefix']} {cum} - Số {i}",
                        loai_san=item["loai"],
                        gia_san_theo_gio=random.choice(item["gia_list"]),
                        hinh_anh=item["anh"],
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