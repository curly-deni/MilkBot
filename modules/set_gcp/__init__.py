import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BrowserControl:
    def __init__(self, bot):

        self.bot = bot

        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument(
            "--user-data-dir=" + self.bot.settings["chrome_profile_path"]
        )
        # chrome_options.headless = True
        chrome_options.add_argument(
            "--profile-directory=" + self.bot.settings["chrome_profile_name"]
        )

        if self.bot.settings["chrome_bin_location"] != "":
            chrome_options.binary_location = self.bot.settings["chrome_bin_location"]
        self.browser = uc.Chrome(options=chrome_options)

        self.gcp = self.bot.settings["gcp"]

    def set_gcp(self, script_id: str) -> None:
        app_script_url = f"https://script.google.com/home/projects/{script_id}/settings"

        self.browser.get(app_script_url)

        change_button = WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'Изменить тип проекта')]")
            )
        )

        change_button.click()

        gcp_id_input = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "i11"))
        )

        gcp_id_button = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'Сохранить')]")
            )
        )

        gcp_id_input.send_keys(self.gcp)
        gcp_id_button.click()
