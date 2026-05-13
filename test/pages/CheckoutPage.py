from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re


class CheckoutPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        self.tong_tien_locator = (By.CSS_SELECTOR, "h2.text-danger.fw-bold")
        self.nut_xac_nhan_locator = (By.CSS_SELECTOR, "button[type='submit']")

    def lay_tong_tien(self):
        element = self.wait.until(EC.visibility_of_element_located(self.tong_tien_locator))
        text_gia = element.text
        number_only = re.sub(r'\D', '', text_gia)
        return float(number_only)

    def click_xac_nhan(self):
        nut = self.wait.until(EC.presence_of_element_located(self.nut_xac_nhan_locator))

        self.driver.execute_script("arguments[0].scrollIntoView(true);", nut)

        self.driver.execute_script("arguments[0].click();", nut)
