import pytest
import hashlib
from sqlalchemy.exc import IntegrityError
from app.auth.dao import add_user, check_existing_user
from app.auth.dao import get_user_by_id
from app.auth.views import load_user
from app.models import NguoiDung
from test.test_base import test_client,test_session, test_app, mock_cloudinary

class FileAnhGia:
    filename = 'anh_dai_dien.png'

def test_dki_thanh_cong(test_session):
    add_user(name='Nguyễn Văn A', username='nva123', password='password123',
             phone='0123456789', email='nva@gmail.com', avatar=None)

    user = NguoiDung.query.filter(NguoiDung.ten_nd == 'nva123').first()

    assert user
    assert user.ho_ten == 'Nguyễn Văn A'
    assert user.so_dien_thoai == '0123456789'
    assert user.email == 'nva@gmail.com'
    assert user.mat_khau == str(hashlib.md5('password123'.encode('utf-8')).hexdigest())

def test_lay_user_bang_id(test_session):
    add_user(name='Nguyễn D', username='user_d', password='123', phone='0111111111', email='d@gmail.com')
    user = NguoiDung.query.filter(NguoiDung.ten_nd == 'user_d').first()

    ket_qua = get_user_by_id(user.id)

    assert ket_qua.ho_ten == 'Nguyễn D'

@pytest.mark.parametrize('dup_username, dup_phone, dup_email, expected_error', [
    ('goc_user', '0999999999', 'khac@gmail.com', 'Tên đăng nhập đã tồn tại!'),
    ('khac_user', '0123456789', 'khac2@gmail.com', 'Số điện thoại này đã được đăng ký!'),
    ('khac_user2', '0888888888', 'goc@gmail.com', 'Email này đã được đăng ký!')
])
def test_thong_tin_bi_trung(dup_username, dup_phone, dup_email, expected_error, test_session):
    add_user(name='User Gốc', username='goc_user', password='123aAAAAAAA', phone='0123456789', email='goc@gmail.com')

    with pytest.raises(Exception) as excinfo:
        add_user(name='Người Mới', username=dup_username, password='123aAAAAAAA', phone=dup_phone, email=dup_email)

    assert str(excinfo.value) == expected_error

def test_them_avatar(test_session, mock_cloudinary):
    file_anh = FileAnhGia()
    add_user(name='Trần B', username='tranb', password='123',
             phone='0987654321', email='tranb@gmail.com', avatar=file_anh)

    user = NguoiDung.query.filter(NguoiDung.ten_nd == 'tranb').first()

    assert user.avatar == 'https://fake-avatar.png'

def test_loi_upload_anh(test_session, monkeypatch):
    file_anh = FileAnhGia()

    with pytest.raises(Exception) as excinfo:
        add_user(name='Nguyễn E', username='user_e', password='123',
                 phone='0222222222', email='e@gmail.com', avatar=file_anh)

    assert str(excinfo.value) == 'Lỗi khi tải ảnh đại diện lên máy chủ!'

def test_loi_database(test_session, monkeypatch):
    def fake_commit():
        raise IntegrityError("DB Error", params={}, orig=None)
    monkeypatch.setattr('app.extention.db.session.commit', fake_commit)

    with pytest.raises(Exception) as excinfo:
        add_user(name='B', username='ub', password='123', phone='0808080808', email='b@gmail.com')

    assert str(excinfo.value) == 'Lỗi hệ thống, không thể lưu dữ liệu!'

def test_kiem_tra_ton_tai(test_session):
    add_user(name='Lê Thị C', username='ltc', password='123',
             phone='0111222333', email='ltc@gmail.com')

    assert check_existing_user('ltc', '0000000000', 'khac@gmail.com') == True
    assert check_existing_user('khac', '0111222333', 'khac@gmail.com') == True
    assert check_existing_user('khac', '0000000000', 'ltc@gmail.com') == True
    assert check_existing_user('moi', '0999999999', 'moi@gmail.com') == False


def test_dang_ky_thanh_cong(test_client, test_session):
    data_gui_len = {
        'name': 'Test',
        'username': 'test123',
        'email': 'test@gmail.com',
        'phone': '0123456789',
        'password': 'password123',
        'confirm': 'password123'
    }

    response = test_client.post('/register', data=data_gui_len)

    assert response.status_code == 302
    assert '/login' in response.headers['Location']


@pytest.mark.parametrize('form_data, loi_mong_doi', [
    ({'name': '', 'username': 'a', 'email': 'a@a.com', 'phone': '0123456789', 'password': '123456',
      'confirm': '123456'}, 'Vui lòng điền đầy đủ tất cả các thông tin!'),
    ({'name': 'A', 'username': 'a', 'email': 'sai_email', 'phone': '0123456789', 'password': '123456',
      'confirm': '123456'}, 'Địa chỉ Email không hợp lệ!'),
    ({'name': 'A', 'username': 'a', 'email': 'a@a.com', 'phone': '123', 'password': '123456', 'confirm': '123456'},
     'Số điện thoại phải có 10 chữ số và bắt đầu bằng số 0!'),
    ({'name': 'A', 'username': 'a', 'email': 'a@a.com', 'phone': '0123456789', 'password': '123', 'confirm': '123'},
     'Mật khẩu phải có ít nhất 6 ký tự!'),
    ({'name': 'A', 'username': 'a', 'email': 'a@a.com', 'phone': '0123456789', 'password': '123456',
      'confirm': '1234567'}, 'Mật khẩu xác nhận không khớp!')
])
def test_dang_ky_loi_form(test_client, form_data, loi_mong_doi):
    response = test_client.post('/register', data=form_data)

    html = response.get_data(as_text=True)

    assert loi_mong_doi in html


def test_dang_ky_trung_thong_tin(test_client, test_session):
    add_user(name='View Gốc', username='view_goc', password='123', phone='0999999999', email='viewgoc@gmail.com')

    form_data = {
        'name': 'Kẻ Mạo Danh', 'username': 'view_goc', 'email': 'viewgoc@gmail.com',
        'phone': '0999999999', 'password': 'password123', 'confirm': 'password123'
    }

    response = test_client.post('/register', data=form_data)
    html = response.get_data(as_text=True)

    assert 'Tên đăng nhập, Email hoặc Số điện thoại đã được sử dụng!' in html


def test_logout(test_client):
    response = test_client.get('/logout')

    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_load_user(test_session):
    add_user(name='Nguyễn F', username='user_f', password='123', phone='0333333333', email='f@gmail.com')
    user = NguoiDung.query.filter(NguoiDung.ten_nd == 'user_f').first()

    ket_qua = load_user(user.id)

    assert ket_qua.ho_ten == 'Nguyễn F'