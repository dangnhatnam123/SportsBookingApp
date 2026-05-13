from test.pages.BasePage import BasePage
from selenium.webdriver.common.by import By


class CheckoutPage(BasePage):

    CONFIRM_BUTTON = (
        By.XPATH,
        "//button[contains(text(),'Xác nhận')]"
    )

    TOTAL_PRICE = (
        By.CLASS_NAME,
        'text-success'
    )

    def click_confirm(self):
        self.click(*self.CONFIRM_BUTTON)

    def get_total_price(self):
        return self.find(*self.TOTAL_PRICE).text