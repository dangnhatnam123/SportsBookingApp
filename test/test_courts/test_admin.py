# import pytest
# from datetime import datetime, timedelta, time
# from app.courts import dao
# from app.models import San, DatLich, NguoiDung, VaiTro, LoaiSan
# from app.test_courts.test_base import test_session, test_client,test_app
# import hashlib
#
# @pytest.fixture()
# def setup_admin_data(test_session):
#     pw = str(hashlib.md5('123456'.encode('utf-8')).hexdigest())
#     admin = NguoiDung(ho_ten="Admin", ten_nd="admin", mat_khau=pw, vai_tro=VaiTro.QUAN_LY)
#     s1 = San(ten_san="Sân Chảo Lửa", loai_san=LoaiSan.BONG_DA, gia_san_theo_gio=100000)
#     s2 = San(ten_san="Sân Lành Mạnh", loai_san=LoaiSan.CAU_LONG, gia_san_theo_gio=80000)
#
#     test_session.add_all([admin, s1, s2])
#     test_session.commit()
#
#     return {'admin': admin, 'san1': s1, 'san2': s2}
#
#
# def test_load_all_san(setup_admin_data):
#     danh_sach = dao.load_all_san()
#     assert len(danh_sach) >= 2
#
#
# def test_add_san_moi(test_session):
#     dao.add_san_moi("Sân Cỏ Nhân Tạo", LoaiSan.BONG_DA, 120000)
#     san = San.query.filter_by(ten_san="Sân Cỏ Nhân Tạo").first()
#     assert san is not None
#
#
# def test_kiem_tra_lich_dat(setup_admin_data, test_session):
#     san_id = setup_admin_data['san1'].id
#     assert dao.kiem_tra_lich_dat(san_id) is False
#
#     ngay_mai = datetime.now() + timedelta(days=1)
#     lich = DatLich(ma_nd=setup_admin_data['admin'].id,
#                    ma_san=san_id,
#                    ngay_choi=ngay_mai.date(),
#                    gio_bd=time(10, 0),
#                    gio_kt=time(11, 0))
#     test_session.add(lich)
#     test_session.commit()
#
#     assert dao.kiem_tra_lich_dat(san_id) is True
#
#
# def test_xoa_san(setup_admin_data, test_session):
#     san_id = setup_admin_data['san2'].id
#     dao.xoa_san(san_id)
#     assert dao.get_san(san_id) is None
#
#
# def test_get_san(setup_admin_data):
#     san = dao.get_san(setup_admin_data['san1'].id)
#     assert san.ten_san == "Sân Chảo Lửa"
#
#
# def test_update_san(setup_admin_data, test_session):
#     san_id = setup_admin_data['san1'].id
#     dao.update_san(san_id, "Sân Mới Đổi", LoaiSan.TENNIS, 200000)
#     san = dao.get_san(san_id)
#     assert san.ten_san == "Sân Mới Đổi"
#     assert san.loai_san == LoaiSan.TENNIS
#
#
# def test_check_ten_san(setup_admin_data):
#     assert dao.check_ten_san("Sân Chảo Lửa") is True
#     assert dao.check_ten_san("Sân Vui Vẻ") is False
#     san_id = setup_admin_data['san1'].id
#     assert dao.check_ten_san("Sân Chảo Lửa", exclude_id=san_id) is False
#
#
# def test_view_base(test_client):
#     assert test_client.get('/').status_code == 200
#     assert test_client.get('/dieu-khoan').status_code == 200
#     assert test_client.get('/gioi-thieu').status_code == 200
#
#
# def test_view_manage_san(test_client, setup_admin_data, monkeypatch):
#     test_client.post('/login', data={'username': 'admin', 'password': '123456'})
#
#     res = test_client.get('/admin/manage_san')
#     assert res.status_code == 200
#
#     monkeypatch.setattr('app.courts.dao.load_all_san', lambda: (_ for _ in ()).throw(Exception("Lỗi Test")))
#     res_err = test_client.get('/admin/manage_san')
#     assert res_err.status_code == 200
#
#
# def test_view_add_san(test_client, setup_admin_data, monkeypatch):
#     """Phủ dòng 36-51: Thêm sân (Trùng tên, Thành công, Lỗi Exception)"""
#     test_client.post('/login', data={'username': 'admin_vip', 'password': '123456'})
#
#     # Trùng tên
#     res_trung = test_client.post('/admin/add-san',
#                                  data={'ten_san': 'Sân Chảo Lửa', 'loai_san': 'Bóng đá', 'gia': 100000},
#                                  follow_redirects=True)
#     assert 'đã tồn tại trong hệ thống' in res_trung.data.decode('utf-8')
#
#     # Thành công
#     res_ok = test_client.post('/admin/add-san', data={'ten_san': 'Sân Bóng Rổ 1', 'loai_san': 'Bóng rổ', 'gia': 50000},
#                               follow_redirects=True)
#     assert 'Thêm sân thành công!' in res_ok.data.decode('utf-8')
#
#     # Lỗi Exception (Ép hàm add_san_moi văng lỗi)
#     monkeypatch.setattr('app.courts.dao.add_san_moi', lambda *args: (_ for _ in ()).throw(Exception("DB Error")))
#     res_err = test_client.post('/admin/add-san', data={'ten_san': 'Sân Đang Lỗi', 'loai_san': 'Bóng đá', 'gia': 10},
#                                follow_redirects=True)
#     assert 'thêm sân thất bại' in res_err.data.decode('utf-8')
#
#
# def test_view_delete_san(test_client, setup_admin_data, test_session, monkeypatch):
#     """Phủ dòng 54-64: Xóa sân (Có lịch đặt, Thành công, Lỗi Exception)"""
#     test_client.post('/login', data={'username': 'admin_vip', 'password': '123456'})
#     san1_id = setup_admin_data['san1'].id
#     san2_id = setup_admin_data['san2'].id
#
#     # 1. Bị chặn do có lịch đặt
#     ngay_mai = datetime.now() + timedelta(days=1)
#     lich = DatLich(ma_nd=setup_admin_data['admin'].id, ma_san=san1_id, ngay_choi=ngay_mai.date(), gio_bd='10:00',
#                    gio_kt='11:00')
#     test_session.add(lich)
#     test_session.commit()
#
#     res_co_lich = test_client.post(f'/admin/delete-san/{san1_id}', follow_redirects=True)
#     assert 'Sân đã có lịch đặt trong tương lai. Không thể xóa!' in res_co_lich.data.decode('utf-8')
#
#     # 2. Xóa thành công
#     res_ok = test_client.post(f'/admin/delete-san/{san2_id}', follow_redirects=True)
#     assert 'Đã xóa sân thành công!' in res_ok.data.decode('utf-8')
#
#     # 3. Lỗi Exception
#     monkeypatch.setattr('app.courts.dao.xoa_san', lambda x: (_ for _ in ()).throw(Exception("DB Error")))
#     res_err = test_client.post(f'/admin/delete-san/{san1_id}', follow_redirects=True)  # Lúc này DB ảo đã có lỗi
#     assert 'Lỗi hệ thống' in res_err.data.decode('utf-8')
#
#
# def test_view_edit_san(test_client, setup_admin_data, monkeypatch):
#     """Phủ dòng 68-82: Sửa sân (Trùng tên, Thành công, Lỗi Exception)"""
#     test_client.post('/login', data={'username': 'admin_vip', 'password': '123456'})
#     san1_id = setup_admin_data['san1'].id
#
#     # Trùng tên (đổi sân 1 thành tên của sân 2)
#     res_trung = test_client.post(f'/admin/edit-san/{san1_id}',
#                                  data={'ten_san': 'Sân Lành Mạnh', 'loai_san': 'Bóng đá', 'gia': 100},
#                                  follow_redirects=True)
#     assert 'đã được sử dụng' in res_trung.data.decode('utf-8')
#
#     # Thành công
#     res_ok = test_client.post(f'/admin/edit-san/{san1_id}',
#                               data={'ten_san': 'Tên Mới Toanh', 'loai_san': 'Bóng đá', 'gia': 100},
#                               follow_redirects=True)
#     assert 'Cập nhật thông tin sân thành công!' in res_ok.data.decode('utf-8')
#
#     # Lỗi Exception
#     monkeypatch.setattr('app.courts.dao.update_san', lambda *args: (_ for _ in ()).throw(Exception("DB Error")))
#     res_err = test_client.post(f'/admin/edit-san/{san1_id}',
#                                data={'ten_san': 'Tên Test Lỗi', 'loai_san': 'Bóng đá', 'gia': 100},
#                                follow_redirects=True)
#     assert 'Lỗi cập nhật' in res_err.data.decode('utf-8')