import hashlib
import random
from datetime import date, timedelta, time

from app.extention import db
from app import app
from app.models import NguoiDung, LoaiSan, San, VaiTro, TrangThaiDL, DatLich

if __name__ == '__main__':
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    with app.app_context():
        db.drop_all()
        db.create_all()

        pwd = str(hashlib.md5('12345678'.encode('utf-8')).hexdigest())

        admin = NguoiDung(ho_ten='Admin Hệ Thống', ten_nd='admin', mat_khau=pwd, vai_tro=VaiTro.QUAN_LY)
        user1 = NguoiDung(ho_ten='Nguyễn Công Phượng', ten_nd='user1', mat_khau=pwd,so_dien_thoai = '0373548687', vai_tro=VaiTro.NHAN_VIEN)
        user2 = NguoiDung(ho_ten='Lý Hoàng Nam', ten_nd='user2', mat_khau=pwd,so_dien_thoai = '0373548688', vai_tro=VaiTro.NGUOI_DUNG)


        db.session.add_all([admin, user1, user2])
        db.session.commit()

        data_set = [
            {
                "cums": ["Chảo Lửa", "Hoa Lư", "Tao Đàn", "Phú Thọ", "K34", "Thành Phát", "An Khang", "Bách Khoa",
                         "Mỹ Đình", "Thống Nhất"],
                "loai": LoaiSan.BONG_DA,
                "anh": "https://hoanghamobile.com/tin-tuc/wp-content/uploads/2023/09/hinh-nen-bong-da-49.jpg",
                "gia_list": [30000, 40000, 50000, 60000],
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
                "gia_list": [60000, 90000, 30000],
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