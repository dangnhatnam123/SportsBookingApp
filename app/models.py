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
                "anh": "https://hoanghamobile.com/tin-tuc/wp-content/uploads/2023/09/hinh-nen-bong-da-49.jpg",
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
            gio_b = random.randint(6, 19)
            phut_b = random.choice([0, 30])
            gio_k = gio_b + random.randint(1, 3)
            phut_k = random.choice([0, 30])
            if (gio_k - gio_b == 1) and (phut_b == 30) and (phut_k == 0):
                phut_k = 30
            slot_key = (ngay_pick, san_chon.id, gio_b)
            if slot_key in used_slots:
                continue
            used_slots.add(slot_key)
            user_daily_counts[user_date_key] = user_daily_counts.get(user_date_key, 0) + 1
            trang_thai_rand = random.choice([TrangThaiDL.CHUA_HOAN_THANH, TrangThaiDL.DA_HOAN_THANH])

            lich = DatLich(
                ngay_choi=ngay_pick,
                gio_bd=time(gio_b, phut_b),
                gio_kt=time(gio_k, phut_k),
                ma_nd=u_id,
                ma_san=san_chon.id,
                trang_thai=trang_thai_rand
            )
            lich_mau.append(lich)

        db.session.add_all(lich_mau)
        db.session.commit()

        print("Khởi tạo Database và dữ liệu mẫu thành công!")