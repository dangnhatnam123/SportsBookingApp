import time

from test.pages.LoginPage import LoginPage
from test.test_base import driver
from test.pages.HomePage import HomePage
from selenium.webdriver.common.by import By


def test_home_search_form(driver):
    home = HomePage(driver=driver)
    home.open_page()
    time.sleep(1)

    home.search_san('BONG_DA', '09/06/2026', '06:00', '08:30')
    time.sleep(2)

    assert '/search' in driver.current_url
    assert 'loai_san=BONG_DA' in driver.current_url

def test_home_nav_gioi_thieu(driver):
    home = HomePage(driver=driver)
    home.open_page()
    time.sleep(1)

    home.click_gioi_thieu()
    time.sleep(1)

    assert '/gioi-thieu' in driver.current_url

def test_home_nav_dieu_khoan(driver):
    home = HomePage(driver=driver)
    home.open_page()
    time.sleep(1)

    home.click_dieu_khoan()
    time.sleep(1)

    assert '/dieu-khoan' in driver.current_url

def test_home_dropdown_bong_da(driver):
    home = HomePage(driver=driver)
    home.open_page()
    time.sleep(1)

    home.click_submenu_bong_da()
    time.sleep(1)

    assert '/search?loai_san=BONG_DA' in driver.current_url


def test_click_dat_san_se_yeu_cau_login(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    time.sleep(1)

    login.login('user1', '12345678')
    time.sleep(2)

    home = HomePage(driver=driver)
    home.open_page()
    time.sleep(1)

    dat_san_menu = driver.find_element(By.CSS_SELECTOR, '.main-menu a[href="/search"]')
    dat_san_menu.click()
    time.sleep(1)

    assert '/search' in driver.current_url
    assert 'login' not in driver.current_url