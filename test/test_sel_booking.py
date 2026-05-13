import time

from test.pages.HomePage import HomePage
from test.pages.LoginPage import LoginPage
from test.test_base import driver
from selenium.webdriver.common.by import By

from test.pages.SearchBookPage import SearchBookPage


def test_search_filter_sidebar(driver):
    search_page = SearchBookPage(driver=driver)
    search_page.open_page()

    search_page.loc_nhanh_bong_da()
    time.sleep(1)

    assert 'loai_san=BONG_DA' in driver.current_url

def test_search_pagination(driver):
    search_page = SearchBookPage(driver=driver)
    search_page.open_page()
    page_2_link = driver.find_element(By.LINK_TEXT, '2')
    page_2_link.click()
    time.sleep(1)

    assert 'page=2' in driver.current_url


def test_full_booking_with_popup(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login('user1', '12345678')
    time.sleep(1)

    home = HomePage(driver=driver)
    home.open_page()
    home.search_san('BONG_DA', '09/06/2026', '06:30', '08:30')
    time.sleep(2)

    search_page = SearchBookPage(driver=driver)
    search_page.bam_dat_ngay_dau_tien()
    time.sleep(1)

    modal_title = driver.find_element(By.CSS_SELECTOR, '.modal.show .modal-title')
    assert 'Xác nhận đặt sân' in modal_title.text

    search_page.bam_xac_nhan_tren_popup()
    time.sleep(2)

    assert '/checkout/' in driver.current_url


def test_click_nut_chi_tiet_san(driver):
    search_page = SearchBookPage(driver=driver)
    search_page.open_page()
    time.sleep(1)
    search_page.bam_chi_tiet_dau_tien()
    time.sleep(2)

    assert '/san/' in driver.current_url

    print(f"Đã vào trang: {driver.current_url}")