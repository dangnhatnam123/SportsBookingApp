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


class TrangThaiDL(UserEnum):
    DA_HOAN_THANH = "Đã Hoàn Thành"
    CHUA_HOAN_THANH = "Chưa Hoàn Thành"
    DA_HUY = "Đã Hủy"


class TrangThaiHoaDon(UserEnum):
    DA_THANH_TOAN = "Đã Thanh Toán"
    CHUA_THANH_TOAN = "Chưa Thanh Toán"


class NguoiDung(BaseModel, UserMixin):
    __tablename__ = 'nguoi_dung'
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
    ten_san = Column(String(50), nullable=False, unique=True)
    loai_san = Column(Enum(LoaiSan), nullable=False)
    gia_san_theo_gio = Column(Float, default=100000)
    hinh_anh = Column(String(255), default='https://images.unsplash.com/photo-1518605368461-1e1e38ce71bd?q=80&w=800')

    dat_lichs = relationship('DatLich', back_populates='san', lazy=True)

    def __str__(self):
        return self.ten_san


class DatLich(BaseModel):
    __tablename__ = 'dat_lich'
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
        user1 = NguoiDung(ho_ten='Nguyễn Công Phượng', ten_nd='user1', mat_khau=pwd, vai_tro=VaiTro.NHAN_VIEN)
        user2 = NguoiDung(ho_ten='Lý Hoàng Nam', ten_nd='user2', mat_khau=pwd, vai_tro=VaiTro.NGUOI_DUNG)
        user3 = NguoiDung(ho_ten='Trần Văn Tèo', ten_nd='user3', mat_khau=pwd, vai_tro=VaiTro.NGUOI_DUNG)
        user4 = NguoiDung(ho_ten='Lê Thị Nở', ten_nd='user4', mat_khau=pwd, vai_tro=VaiTro.NGUOI_DUNG)
        user5 = NguoiDung(ho_ten='Trần Văn Tí', ten_nd='user5', mat_khau=pwd, vai_tro=VaiTro.NGUOI_DUNG)
        user6 = NguoiDung(ho_ten='Lê Thị Ninh', ten_nd='user6', mat_khau=pwd, vai_tro=VaiTro.NGUOI_DUNG)

        db.session.add_all([admin, user1, user2,user3, user4, user5, user6])
        db.session.commit()

        data_set = [
            {
                "cums": ["Chảo Lửa", "Hoa Lư", "Tao Đàn", "Phú Thọ", "K34", "Thành Phát", "An Khang", "Bách Khoa",
                         "Mỹ Đình", "Thống Nhất"],
                "loai": LoaiSan.BONG_DA,
                "anh": "data:image/jpeg;base64,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",
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

        danh_sach_san = []
        for item in data_set:
            for cum in item["cums"]:
                for i in range(1, 5):

                    s = San(
                        ten_san=f"{item['prefix']} {cum} - Số {i}",
                        loai_san=item["loai"],
                        gia_san_theo_gio=random.choice(item["gia_list"]),
                        hinh_anh=item["anh"]
                    )
                    danh_sach_san.append(s)

        db.session.add_all(danh_sach_san)
        db.session.commit()


        hom_nay = date.today()
        tat_ca_user = NguoiDung.query.filter(NguoiDung.vai_tro == VaiTro.NGUOI_DUNG).all()
        danh_sach_user_id = [u.id for u in tat_ca_user]
        tat_ca_san = San.query.all()
        lich_mau = []
        used_slots = set()
        user_daily_counts = {}
        for _ in range(200):
            if len(lich_mau) >= 40:
                break
            u_id = random.choice(danh_sach_user_id)
            san_chon = random.choice(tat_ca_san)
            ngay_pick = hom_nay + timedelta(days=random.randint(0, 7))
            user_date_key = (u_id, ngay_pick)
            if user_daily_counts.get(user_date_key, 0) >= 3:
                continue
            gio_b = random.randint(6, 20)
            gio_k = gio_b + 1
            slot_key = (ngay_pick, san_chon.id, gio_b)
            if slot_key in used_slots:
                continue
            used_slots.add(slot_key)
            user_daily_counts[user_date_key] = user_daily_counts.get(user_date_key, 0) + 1
            trang_thai_rand = random.choice([TrangThaiDL.CHUA_HOAN_THANH, TrangThaiDL.DA_HOAN_THANH])
            lich = DatLich(
                ngay_choi=ngay_pick,
                gio_bd=time(gio_b, 0),
                gio_kt=time(gio_k, 0),
                ma_nd=u_id,
                ma_san=san_chon.id,
                trang_thai=trang_thai_rand
            )
            lich_mau.append(lich)

        db.session.add_all(lich_mau)
        db.session.commit()

        print("Khởi tạo Database và dữ liệu mẫu thành công!")