from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import NoReturn


class BrowserControl:
    def __init__(self, firefox_profile: str):

        firefox_options = webdriver.FirefoxOptions()
        firefox_options.headless = True
        profile = webdriver.FirefoxProfile(firefox_profile)

        self.browser = webdriver.Firefox(
            options=firefox_options, firefox_profile=profile
        )

    def set_gcp(self, gcp: int, script_id: str) -> NoReturn:

        app_script_url = f"https://script.google.com/home/projects/{script_id}/settings"

        self.browser.get(app_script_url)

        change_button = WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'Изменить тип проекта')]")
            )
        )
        # actions.move_to_element(change_button).perform()
        change_button.click()

        gcp_id_input = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "i11"))
        )
        # actions.move_to_element(gcp_id_input).perform()

        gcp_id_input.send_keys(gcp)

        gcp_id_button = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'Сохранить')]")
            )
        )
        # actions.move_to_element(gcp_id_button).perform()
        gcp_id_button.click()
