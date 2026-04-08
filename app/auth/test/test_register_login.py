import pytest
from app.auth import dao
from app.auth.test.test_base import test_client,test_session,test_app
from app.models import NguoiDung


def test_dki_thanh_cong(test_session):
    dao.add_user(name="DangNem", username= "nemnem" , password= "Nemnem123")
    u = NguoiDung.query.filter(NguoiDung.ten_nd == "nemnem").first()

    assert u is not None
    assert u.ten_nd == "nemnem"

@pytest.mark.parametrize('password',[
    '1234567',
    '11111111',
    'aaaaaaaa',
    '        '
])

def test_dki_MK_sai(test_session,password):
    with pytest.raises(ValueError):
        dao.add_user(name="Nem", username= "nemnem1", password= password)

def test_trung_username(test_session):
    dao.add_user(name="Nem", username= "nemnem", password= "Nemnem123")
    with pytest.raises(Exception):
        dao.add_user(name="Nam", username= "nemnem", password= "Nemnem123")

def test_MK_khi_login(test_session):
    dao.add_user(name="Nem", username= "nemnem", password= "Nemnem123")

    assert dao.auth_user("nemnem","Nemnem123") is not None
    assert dao.auth_user("nemnem","Nem123456") is None
    assert dao.auth_user("nem111","Nemnem123") is None

