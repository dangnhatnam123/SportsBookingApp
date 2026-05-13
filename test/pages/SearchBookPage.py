from test.pages.BasePage import BasePage
from selenium.webdriver.common.by import By


class SearchBookPage(BasePage):
    URL = 'http://127.0.0.1:5000/search'

    LOAI_SAN_SELECT = (By.NAME, 'loai_san')
    NGAY_INPUT = (By.NAME, 'ngay')
    GIO_BD_SELECT = (By.NAME, 'gio_bd')
    SEARCH_BUTTON = (By.CSS_SELECTOR, 'button[type="submit"]')
    BONG_DA_FILTER = (By.CSS_SELECTOR, 'a[href="?loai_san=BONG_DA"]')
    DAT_NGAY_BTN = (By.CSS_SELECTOR, '.san-card .btn-success')
    CONFIRM_MODAL_PAY_BTN = (By.CSS_SELECTOR, '.modal.show .btn-success')
    CHI_TIET_BTN = (By.CSS_SELECTOR, '.san-card .btn-outline-primary')

    def open_page(self):
        self.open(self.URL)

    def loc_nhanh_bong_da(self):
        self.click(*self.BONG_DA_FILTER)

    def bam_dat_ngay_dau_tien(self):
        self.click(*self.DAT_NGAY_BTN)

    def bam_xac_nhan_tren_popup(self):
        self.click(*self.CONFIRM_MODAL_PAY_BTN)

    def bam_chi_tiet_dau_tien(self):
        self.click(*self.CHI_TIET_BTN)