import pytest
from app.auth import dao
from app.test.test_base import test_client,test_session,test_app ,mock_cloudinary
from app.auth.views import load_user
from app.models import NguoiDung, VaiTro


def test_dki_thanh_cong(test_session):
    dao.add_user(name="DangNem", username= "nemnem" , password= "Nemnem123")
    u = NguoiDung.query.filter(NguoiDung.ten_nd == "nemnem").first()

    assert u is not None
    assert u.ten_nd == "nemnem"

def test_trung_username(test_session):
    dao.add_user(name="Nem", username= "nemnem", password= "Nemnem123")
    with pytest.raises(Exception, match='Tên đăng nhập đã tồn tại!'):
        dao.add_user(name="Nam", username= "nemnem", password= "Nemnem133")

def test_MK_khi_login(test_session):
    dao.add_user(name="Nem", username= "nemnem", password= "Nemnem123")

    assert dao.auth_user("nemnem","Nemnem123") is not None
    assert dao.auth_user("nemnem","Nem123456") is None
    assert dao.auth_user("nem111","Nemnem123") is None

def test_dang_nhap_route_thanh_cong(test_session,test_client):
    dao.add_user(name="Nem1", username= "nemnem", password= "Nemnem123")
    response = test_client.post("/login", data={"username":"nemnem","password":"Nemnem123"})

    assert response.status_code == 302
    assert response.headers["Location"] == "/"

def test_khoang_trang(test_session):
    dao.add_user(name="  Dang Nem   ", username= "nem   ", password= "   12345678   ")
    u = dao.auth_user(username="nem", password="12345678")

    assert u is not None
    assert u.ho_ten == "Dang Nem"
    assert u.ten_nd== "nem"

def test_get_user_by_id(test_session):
    dao.add_user(name="Nem", username= "nemdeng", password= "123456789")
    u_created = dao.auth_user(username="nemdeng", password="123456789")

    u_found = dao.get_user_by_id(u_created.id)

    assert u_found is not None
    assert u_found.ten_nd == "nemdeng"
    assert dao.get_user_by_id(99999) is None

def test_avt(test_session,mock_cloudinary):
    dao.add_user(name="Namavt", username="namavt", password="12345678", avatar="anh_cua_nam.png")
    u = dao.auth_user(username="namavt", password="12345678")

    assert u is not None
    assert u.avatar == 'https://fake-avatar.png'

def test_chuyen_huong_trang_truoc(test_session,test_client):
    u = dao.add_user(name="Nam",username="nemnem", password="12345678")
    res = test_client.post('/login?next=/search', data={'username': 'nemnem', 'password': '12345678'})
    assert res.status_code == 302
    assert '/search' in res.headers['Location']


def test_login_role_admin(test_client, test_session):
    dao.add_user(name="Admin", username="admin", password="11111111")
    u = NguoiDung.query.filter_by(ten_nd="admin").first()
    u.vai_tro = VaiTro.QUAN_LY
    test_session.commit()

    res = test_client.post('/login', data={'username': 'admin', 'password': '11111111'})
    assert res.status_code == 302
    assert res.headers['Location'] == '/admin/manage_san'

def test_dang_nhap_sai_pass(test_client, test_session):
    dao.add_user(name="Nam", username="nam", password="33333333")
    res = test_client.post('/login', data={'username': 'nam', 'password': '12345678'})
    assert res.status_code == 200
    assert 'Tên đăng nhập hoặc mật khẩu không chính xác!' in res.data.decode('utf-8')


def test_register_2pass_khong_khop(test_client):
    res = test_client.post('/register', data={
        'name': 'Nam', 'username': 'namnem', 'password': '123444', 'confirm': '456123'
    })
    assert res.status_code == 200
    assert 'Mật khẩu xác nhận không khớp!' in res.data.decode('utf-8')


def test_register_thanh_cong_chuyen_trang(test_client, test_session):
    res = test_client.post('/register', data={
        'name': 'Nam', 'username': 'nam', 'password': '12345678', 'confirm': '12345678'
    })
    assert res.status_code == 302
    assert res.headers['Location'] == '/login'


def test_register_trung_username(test_client, test_session):
    dao.add_user(name="Nam 1", username="namnem", password="12345678")
    res = test_client.post('/register', data={
        'name': 'Nam 2', 'username': 'namnem', 'password': '123123123', 'confirm': '123123123'
    })
    assert res.status_code == 200
    assert 'Tên đăng nhập đã tồn tại!' in res.data.decode('utf-8')

def test_logout(test_client):
    res = test_client.get('/logout')
    assert res.status_code == 302
    assert res.headers['Location'] == '/login'


def test_load_user(test_session):
    dao.add_user(name="nem", username="nem", password="123456789")
    u = NguoiDung.query.filter_by(ten_nd="nem").first()

    assert load_user(u.id) is not None


def test_truy_cap_dat_san_khi_chua_login(test_client):
    res = test_client.get('/checkout/1?ngay=2026-05-01&gio_bd=10:00&gio_kt=11:00')
    assert res.status_code == 302
    assert '/login' in res.headers['Location']