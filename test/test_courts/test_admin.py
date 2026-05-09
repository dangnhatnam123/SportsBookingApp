from app.models import San, LoaiSan
from app.courts import dao
from test.test_base import test_client,test_session, test_app, mock_cloudinary,setup_booking_data


def test_lay_danh_sach_tat_ca_san(test_session, setup_booking_data):
    ket_qua = dao.load_all_san()

    assert len(ket_qua) >= 2
    assert ket_qua[0].ten_san == "Sân Chảo Lửa 1"


def test_lay_thong_tin_san_theo_id(test_session, setup_booking_data):
    san_id = setup_booking_data['san1'].id
    san = dao.get_san(san_id)

    assert san is not None
    assert san.ten_san == "Sân Chảo Lửa 1"
    assert dao.get_san(9999) is None


def test_them_san_moi_vao_he_thong(test_session):
    dao.add_san_moi("Sân Cầu Lông VIP", LoaiSan.CAU_LONG, 120000)

    san = San.query.filter_by(ten_san="Sân Cầu Lông VIP").first()
    assert san is not None
    assert san.gia_san_theo_gio == 120000


def test_kiem_tra_ten_san_ton_tai(test_session, setup_booking_data):
    assert dao.check_ten_san("Sân Chảo Lửa 1") is True
    assert dao.check_ten_san("Sân Chảo Lửa 1", exclude_id=setup_booking_data['san1'].id) is False
    assert dao.check_ten_san("Sân Chưa Có") is False


def test_cap_nhat_thong_tin_san_ton_tai(test_session, setup_booking_data):
    san_id = setup_booking_data['san2'].id
    dao.update_san(san_id, "Sân 2 Đã Đổi Tên", LoaiSan.TENNIS, 300000)

    san_sua = dao.get_san(san_id)
    assert san_sua.ten_san == "Sân 2 Đã Đổi Tên"
    assert san_sua.loai_san == LoaiSan.TENNIS


def test_xoa_san_khoi_co_so_du_lieu(test_session, setup_booking_data):
    san_id = setup_booking_data['san2'].id
    dao.xoa_san(san_id)

    assert dao.get_san(san_id) is None


def test_kiem_tra_rang_buoc_lich_dat(test_session, setup_booking_data):
    assert dao.kiem_tra_lich_dat(setup_booking_data['san1'].id) is True
    assert dao.kiem_tra_lich_dat(setup_booking_data['san2'].id) is False


def test_truy_cap_quan_ly_san_voi_quyen_admin(test_client, setup_booking_data):
    test_client.post('/login', data={'username': 'admin', 'password': '123456'})

    response = test_client.get('/admin/manage_san')

    assert response.status_code == 200
    assert "Sân Chảo Lửa 1" in response.data.decode('utf-8')


def test_chan_truy_cap_quan_ly_khi_la_nguoi_dung_thuong(test_client, setup_booking_data):
    test_client.post('/login', data={'username': 'khach', 'password': '123456'})

    response = test_client.get('/admin/manage_san')

    assert response.status_code == 302


def test_quan_ly_san_loi_he_thong_load_danh_sach(test_client, setup_booking_data, monkeypatch):
    test_client.post('/login', data={'username': 'admin', 'password': '123456'})

    def fake_load():
        raise Exception("Sập DB")

    monkeypatch.setattr('app.courts.views.dao.load_all_san', fake_load)

    response = test_client.get('/admin/manage_san')
    assert response.status_code == 200

def test_them_san_moi_thanh_cong(test_client, setup_booking_data):
    test_client.post('/login', data={'username': 'admin', 'password': '123456'})

    response = test_client.post('/admin/add-san', data={
        'ten_san': 'Sân Bóng Mới 100', 'loai_san': 'BONG_DA', 'gia': 150000
    }, follow_redirects=True)

    assert "Thêm sân thành công" in response.data.decode('utf-8')
    assert dao.check_ten_san('Sân Bóng Mới 100') is True


def test_them_san_that_bai_do_trung_ten(test_client, setup_booking_data):
    test_client.post('/login', data={'username': 'admin', 'password': '123456'})

    response = test_client.post('/admin/add-san', data={
        'ten_san': 'Sân Chảo Lửa 1', 'loai_san': 'BONG_DA', 'gia': 100000
    }, follow_redirects=True)

    assert "đã tồn tại trong hệ thống" in response.data.decode('utf-8')


def test_them_san_loi_he_thong(test_client, setup_booking_data, monkeypatch):
    test_client.post('/login', data={'username': 'admin', 'password': '123456'})

    def fake_add(*args, **kwargs): raise Exception("Lỗi DB")

    monkeypatch.setattr('app.courts.views.dao.add_san_moi', fake_add)

    response = test_client.post('/admin/add-san', data={
        'ten_san': 'Sân Lỗi', 'loai_san': 'BONG_DA', 'gia': 100
    }, follow_redirects=True)

    assert "thêm sân thất bại" in response.data.decode('utf-8')


def test_sua_san_thanh_cong(test_client, setup_booking_data):
    test_client.post('/login', data={'username': 'admin', 'password': '123456'})
    san_id = setup_booking_data['san2'].id

    response = test_client.post(f'/admin/edit-san/{san_id}', data={
        'ten_san': 'Sân 2 Cập Nhật', 'loai_san': 'CAU_LONG', 'gia': 99000
    }, follow_redirects=True)

    assert "Cập nhật thông tin sân thành công" in response.data.decode('utf-8')
    assert dao.get_san(san_id).ten_san == "Sân 2 Cập Nhật"


def test_sua_san_that_bai_do_ten_da_duoc_dung(test_client, setup_booking_data):
    test_client.post('/login', data={'username': 'admin', 'password': '123456'})
    san_id = setup_booking_data['san2'].id

    response = test_client.post(f'/admin/edit-san/{san_id}', data={
        'ten_san': 'Sân Chảo Lửa 1', 'loai_san': 'BONG_DA', 'gia': 100
    }, follow_redirects=True)

    assert "đã được sử dụng" in response.data.decode('utf-8')


def test_sua_san_loi_he_thong_khi_update(test_client, setup_booking_data, monkeypatch):
    test_client.post('/login', data={'username': 'admin', 'password': '123456'})
    san_id = setup_booking_data['san2'].id

    def fake_update(*args, **kwargs):
        raise Exception("Lỗi Update DB")

    monkeypatch.setattr('app.courts.views.dao.update_san', fake_update)

    response = test_client.post(f'/admin/edit-san/{san_id}', data={
        'ten_san': 'Sân 2 Lỗi', 'loai_san': 'BONG_DA', 'gia': 100
    }, follow_redirects=True)

    assert "Lỗi cập nhật" in response.data.decode('utf-8')

def test_xoa_san_thanh_cong(test_client, setup_booking_data):
    test_client.post('/login', data={'username': 'admin', 'password': '123456'})
    san_id = setup_booking_data['san2'].id

    response = test_client.post(f'/admin/delete-san/{san_id}', follow_redirects=True)

    assert "Đã xóa sân thành công" in response.data.decode('utf-8')
    assert dao.get_san(san_id) is None


def test_chan_xoa_san_khi_dang_co_lich_dat(test_client, setup_booking_data):
    test_client.post('/login', data={'username': 'admin', 'password': '123456'})
    san_id = setup_booking_data['san1'].id

    response = test_client.post(f'/admin/delete-san/{san_id}', follow_redirects=True)

    assert "Sân đã có lịch đặt trong tương lai" in response.data.decode('utf-8')
    assert dao.get_san(san_id) is not None


def test_xoa_san_loi_he_thong(test_client, setup_booking_data, monkeypatch):
    test_client.post('/login', data={'username': 'admin', 'password': '123456'})

    def fake_xoa(*args, **kwargs): raise Exception("Lỗi DB")

    monkeypatch.setattr('app.courts.views.dao.xoa_san', fake_xoa)

    response = test_client.post(f'/admin/delete-san/{setup_booking_data["san2"].id}', follow_redirects=True)

    assert "Lỗi hệ thống" in response.data.decode('utf-8')

