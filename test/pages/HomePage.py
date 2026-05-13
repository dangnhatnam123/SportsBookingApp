from test.pages.BasePage import BasePage
from selenium.webdriver.common.by import By


class HomePage(BasePage):
    URL = 'http://127.0.0.1:5000/'

    LOAI_SAN_SELECT = (By.NAME, 'loai_san')
    NGAY_INPUT = (By.NAME, 'ngay')
    GIO_BD_SELECT = (By.NAME, 'gio_bd')
    GIO_KT_SELECT = (By.NAME, 'gio_kt')
    SEARCH_BUTTON = (By.CSS_SELECTOR, '.btn-search-yellow')

    GIOI_THIEU_LINK = (By.CSS_SELECTOR, 'a[href="/gioi-thieu"]')
    DIEU_KHOAN_LINK = (By.CSS_SELECTOR, 'a[href="/dieu-khoan"]')

    BONG_DA_SUBMENU = (By.CSS_SELECTOR, 'a[href="/search?loai_san=BONG_DA"]')

    def open_page(self):
        self.open(self.URL)


    def search_san(self, loai_san, ngay, gio_bd, gio_kt):
        self.typing(*self.LOAI_SAN_SELECT, loai_san)
        self.typing(*self.NGAY_INPUT, ngay)
        self.typing(*self.GIO_BD_SELECT, gio_bd)
        self.typing(*self.GIO_KT_SELECT, gio_kt)
        self.click(*self.SEARCH_BUTTON)

    def click_gioi_thieu(self):
        self.click(*self.GIOI_THIEU_LINK)

    def click_dieu_khoan(self):
        self.click(*self.DIEU_KHOAN_LINK)

    def click_submenu_bong_da(self):
        self.click(*self.BONG_DA_SUBMENU)

