import pytest
import time
from test.test_base import driver
from test.pages.LoginPage import LoginPage
from test.pages.CheckoutPage import CheckoutPage


def test_checkout_thanh_toan_dat_san(driver):
    login_page = LoginPage(driver=driver)
    login_page.open_page()
    login_page.login('user1', '12345678')

    time.sleep(2)

    target_url = "http://127.0.0.1:5000/checkout/81?ngay=2026-05-15&gio_bd=09:00&gio_kt=16:30"
    driver.get(target_url)

    checkout = CheckoutPage(driver=driver)

    tong_tien_ui = checkout.lay_tong_tien()
    assert tong_tien_ui == 225000
    print(f"\n[PASS] Tổng tiền khớp: {tong_tien_ui} VNĐ")

    checkout.click_xac_nhan()

    time.sleep(2)
    assert "/process-payment" in driver.current_url or "momo" in driver.current_url.lower()
    print("[PASS] Đã điều hướng đến trang xử lý thanh toán.")


