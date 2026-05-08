import pytest

from app.auth.dao import auth_user, add_user
from app.models import NguoiDung, VaiTro
from test.test_base import test_client, test_session, mock_cloudinary, test_app

def test_dang_nhap_thanh_cong(test_session):
    add_user(name='Lê Văn A', username='levana', password='password123', phone='0111111111', email='a@gmail.com')

    user = auth_user('levana', 'password123')

    assert user is not None
    assert user.ten_nd == 'levana'


def test_dang_nhap_sai_thong_tin(test_session):
    add_user(name='Nguyễn Văn B', username='nguyenvanb', password='password123', phone='0222222222', email='b@gmail.com')

    user_sai_pass = auth_user('nguyenvanb', '111111')
    user_sai_ten = auth_user('nguoila', 'password123')

    assert user_sai_pass is None
    assert user_sai_ten is None


def test_dang_nhap_tai_khoan_bi_khoa(test_session):
    add_user(name='Trần Văn Khóa', username='vankhoa', password='password123', phone='0777777777',
             email='khoa@gmail.com')

    user_khoa = NguoiDung.query.filter(NguoiDung.ten_nd == 'vankhoa').first()
    user_khoa.active = False
    test_session.commit()
    ket_qua = auth_user('vankhoa', 'password123')

    assert ket_qua is None

def test_dang_nhap_du_khoang_trang(test_session):
    add_user(name='Lý Văn C', username='lyvanc', password='password123', phone='0888888888', email='c@gmail.com')
    user = auth_user('   lyvanc   ', '   password123   ')

    assert user is not None
    assert user.ten_nd == 'lyvanc'

def test_mo_trang_dang_nhap(test_client):
    response = test_client.get('/login')

    assert response.status_code == 200


@pytest.mark.parametrize('username, password, loi_mong_doi', [
    ('', '123456', 'Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!'),
    ('tranvanc', '', 'Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!'),
    ('', '', 'Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!'),
    ('tranvanc', 'sai_pass', 'Tên đăng nhập, mật khẩu không chính xác hoặc tài khoản đã bị khóa!'),
    ('nguoi_la', '123456', 'Tên đăng nhập, mật khẩu không chính xác hoặc tài khoản đã bị khóa!')
])
def test_dang_nhap_loi_form(test_client, test_session, username, password, loi_mong_doi):
    add_user(name='Trần Văn C', username='tranvanc', password='123456', phone='0333333333', email='c@gmail.com')

    response = test_client.post('/login', data={'username': username, 'password': password})
    html = response.get_data(as_text=True)

    assert loi_mong_doi in html


def test_view_dang_nhap_thanh_cong_nguoi_dung(test_client, test_session):
    add_user(name='Lê Thị D', username='lethid', password='password123', phone='0444444444', email='d@gmail.com')

    response = test_client.post('/login', data={'username': 'lethid', 'password': 'password123'})

    assert response.status_code == 302
    assert response.headers['Location'] == '/'


def test_dang_nhap_thanh_cong_quan_ly(test_client, test_session):
    add_user(name='Phạm Văn E', username='phamvane', password='password123', phone='0555555555', email='e@gmail.com')

    admin = NguoiDung.query.filter(NguoiDung.ten_nd == 'phamvane').first()
    admin.vai_tro = VaiTro.QUAN_LY
    test_session.commit()

    response = test_client.post('/login', data={'username': 'phamvane', 'password': 'password123'})

    assert response.status_code == 302
    assert '/admin/manage_san' in response.headers['Location']


def test_dang_nhap_chuyen_huong_next(test_client, test_session):
    add_user(name='Đinh Văn F', username='dinhvanf', password='password123', phone='0666666666', email='f@gmail.com')

    response = test_client.post('/login?next=/checkout', data={'username': 'dinhvanf', 'password': 'password123'})

    assert response.status_code == 302
    assert '/checkout' in response.headers['Location']