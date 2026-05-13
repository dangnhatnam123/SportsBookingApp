from test.pages.BasePage import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class AdminPage(BasePage):
    URL = 'http://127.0.0.1:5000/admin/manage_san'

    BTN_THEM_MOI = (By.CSS_SELECTOR, 'button[data-bs-target="#modalThemSan"]')
    INPUT_TEN_THEM = (By.CSS_SELECTOR, '#modalThemSan input[name="ten_san"]')
    SELECT_LOAI_THEM = (By.CSS_SELECTOR, '#modalThemSan select[name="loai_san"]')
    INPUT_GIA_THEM = (By.CSS_SELECTOR, '#modalThemSan input[name="gia"]')
    BTN_LUU_THEM = (By.CSS_SELECTOR, '#modalThemSan button[type="submit"]')

    INPUT_TEN_SUA = (By.CSS_SELECTOR, '.modal.show input[name="ten_san"]')
    BTN_LUU_SUA = (By.CSS_SELECTOR, '.modal.show button[type="submit"]')

    def open_page(self):
        self.open(self.URL)

    def them_san(self, ten, loai, gia):
        wait = WebDriverWait(self.driver, 10)
        self.click(*self.BTN_THEM_MOI)
        time.sleep(1)
        wait.until(EC.visibility_of_element_located(self.INPUT_TEN_THEM))
        self.typing(*self.INPUT_TEN_THEM, ten)
        self.typing(*self.SELECT_LOAI_THEM, loai)
        self.typing(*self.INPUT_GIA_THEM, gia)
        self.click(*self.BTN_LUU_THEM)

    def sua_san_cuoi_cung(self, ten_moi):
        trs = self.driver.find_elements(By.CSS_SELECTOR, 'table tbody tr')
        btn_sua = trs[-1].find_element(By.CSS_SELECTOR, 'button[data-bs-target^="#modalEdit"]')
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_sua)
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].click();", btn_sua)
        time.sleep(1)
        wait = WebDriverWait(self.driver, 10)
        input_ten = wait.until(EC.visibility_of_element_located(self.INPUT_TEN_SUA))
        input_ten.clear()
        input_ten.send_keys(ten_moi)

        # 3. Lưu
        self.click(*self.BTN_LUU_SUA)

    def xoa_san_cuoi_cung(self):
        trs = self.driver.find_elements(By.CSS_SELECTOR, 'table tbody tr')
        btn_xoa = trs[-1].find_element(By.CSS_SELECTOR, 'form button.btn-outline-danger')

        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_xoa)
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].click();", btn_xoa)
        time.sleep(1)
        wait = WebDriverWait(self.driver, 10)
        alert = wait.until(EC.alert_is_present())
        alert.accept()