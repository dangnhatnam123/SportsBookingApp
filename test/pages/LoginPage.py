from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LoginPage:
    URL = 'http://127.0.0.1:5000/login'

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

        self.USERNAME_FIELD = (By.ID, 'username')
        self.PASSWORD_FIELD = (By.ID, 'password')
        self.BTN_LOGIN = (By.CSS_SELECTOR, 'button[type=submit]')

    def open_page(self):
        self.driver.get(self.URL)

    def login(self, username, password):
        user_input = self.wait.until(EC.presence_of_element_located(self.USERNAME_FIELD))
        user_input.clear()
        user_input.send_keys(username)

        try:
            pass_input = self.wait.until(EC.presence_of_element_located(self.PASSWORD_FIELD))
        except:
            pass_input = self.wait.until(EC.presence_of_element_located((By.ID, 'pwd')))

        pass_input.clear()
        pass_input.send_keys(password)

        btn = self.wait.until(EC.element_to_be_clickable(self.BTN_LOGIN))
        btn.click()