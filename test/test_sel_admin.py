import time
from test.test_base import driver
from test.pages.AdminPage import AdminPage
from test.pages.LoginPage import LoginPage


def test_admin_them_sua_xoa_san(driver):
    login_page = LoginPage(driver=driver)
    login_page.open_page()
    login_page.login('admin', '12345678')
    time.sleep(2)

    admin_page = AdminPage(driver=driver)
    admin_page.open_page()
    time.sleep(1)

    ten_san_ban_dau = "Sân Test Tự Động 999"
    admin_page.them_san(ten_san_ban_dau, "BONG_DA", "150000")
    time.sleep(2)

    assert ten_san_ban_dau in driver.page_source

    ten_san_da_sua = "Sân Test Đã Được Đổi Tên"
    admin_page.sua_san_cuoi_cung(ten_san_da_sua)
    time.sleep(2)

    assert ten_san_da_sua in driver.page_source

    admin_page.xoa_san_cuoi_cung()
    time.sleep(2)

    assert ten_san_da_sua not in driver.page_source
    print("Test luồng Admin hoàn thành xuất sắc!")