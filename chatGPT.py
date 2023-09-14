import zipfile
from time import sleep
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import logging
import json

import config
import extension

os.environ['DISPLAY'] = ':0.0'


class ChatGPT:
    _driver: webdriver.Chrome
    _logger: logging

    def __init__(self, update_extension: bool = False, use_proxy: bool = True):
        self._logger = logging.getLogger("chat_bot_logger")
        self._logger.setLevel(logging.INFO)
        handler = logging.FileHandler('ChatGPT_log.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)


        chrome_options: Options = webdriver.ChromeOptions()
        if use_proxy:
            if update_extension:
                if os.path.exists('proxy_auth_plugin.zip'):
                    os.remove('proxy_auth_plugin.zip')
            if not os.path.exists('proxy_auth_plugin.zip'):
                with zipfile.ZipFile('proxy_auth_plugin.zip', 'w') as zp:
                    zp.writestr('manifest.json', extension.manifest_json)
                    zp.writestr('background.js', extension.background_js)
            chrome_options.add_extension('proxy_auth_plugin.zip')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        prefs = {"credentials_enable_service": False,
                 "profile.password_manager_enabled": False}
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--disable-password-manager-reauthentication")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-save-password-bubble")  # отключение менеджера сохранения паролей
        chrome_options.add_argument("--disable-translate")
        chrome_options.add_argument("--disable-autofill-dropdown")

        service = Service(config.PATH_TO_DRIVER)
        self._driver = webdriver.Chrome(options=chrome_options, service=service)
        self._logger.info("driver running")

    def test(self):
        self._driver.get("https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html")
        sleep(10)
        self._driver.get("https://whoer.net")
        sleep(10)

    def authorization(self, wait_time: int = 10) -> bool:
        self._logger.info("authorization  running")
        self._driver.get("https://chat.openai.com/")
        wait = WebDriverWait(self._driver, wait_time)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, config.CHAT_GPT_AUTH_FIRST_BTN)))
        btn = self._driver.find_element(By.CSS_SELECTOR, config.CHAT_GPT_AUTH_FIRST_BTN)
        self._driver.execute_script("arguments[0].click();", btn)
        wait = WebDriverWait(self._driver, wait_time)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, config.CHAT_GPT_AUTH_USER_FIELD)))
        self._driver.find_element(By.CSS_SELECTOR, config.CHAT_GPT_AUTH_USER_FIELD).send_keys(config.CHAT_GPT_USERNAME)
        btn = self._driver.find_element(By.CSS_SELECTOR, config.CHAT_GPT_AUTH_USER_BTN)
        self._driver.execute_script("arguments[0].click();", btn)
        wait = WebDriverWait(self._driver, wait_time)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, config.CHAT_GPT_AUTH_PASSWORD_FIELD)))
        self._driver.find_element(By.CSS_SELECTOR, config.CHAT_GPT_AUTH_PASSWORD_FIELD).send_keys(
            config.CHAT_GPT_PASSWORD)
        btn = self._driver.find_element(By.CSS_SELECTOR, config.CHAT_GPT_AUTH_USER_BTN)
        self._driver.execute_script("arguments[0].click();", btn)
        cookies = self._driver.get_cookies()

        # # Сохраняем куки в файл (например, в формате JSON)
        # with open("cookies.json", "w") as json_file:
        #     json.dump(cookies, json_file)
        self._logger.info("authorization  success")
        sleep(5)
        element = self._driver.find_element(By.CSS_SELECTOR, config.CHAT_GPT_INF_BTN)
        btn = element.find_element(By.TAG_NAME, "button")
        self._logger.info(f"authorization  start working ")
        self._driver.execute_script("arguments[0].click();", btn)
        self._logger.info("authorization  ready for work")
        return True

    def finish_work(self) -> None:
        self._driver.close()
        self._driver.quit()

    def check_authorization(self):
        # to do
        self._logger.info("check_authorization  running")
        self._driver.get("https://chat.openai.com/")
        if not os.path.exists('cookies.json'):
            self._logger.info("check_authorization  none cookies")
            return False

        with open("cookies.json", "r") as json_file:
            cookies = json.load(json_file)

        # Загрузка куков в браузер
        for cookie in cookies:
            self._driver.add_cookie(cookie)
        self._driver.refresh()

    def _waiting_answer(self, try_count: int = 20, sleep_time_for_count: int = 2) -> None:
        self._logger.info(f"waiting_answer  start working ")
        for _ in range(try_count):
            if len(self._driver.find_elements(By.CSS_SELECTOR, config.CHAT_GPT_PROCESSING)) > 0:
                sleep(sleep_time_for_count)
            else:
                self._logger.info(f"waiting_answer  finish working iteration {_}")
                return
        self._logger.info(f"waiting_answer  finish working all iteration")

    def ask_bot(self, question: str) -> str:
        self._logger.info(f"ask_bot  asked {question}")
        element = self._driver.find_element(By.CSS_SELECTOR, config.CHAT_GPT_QUESTION_FIELD)
        element.send_keys(question)
        element.send_keys(Keys.ENTER)
        self._waiting_answer()
        element = self._driver.find_elements(By.CSS_SELECTOR, config.CHAT_GPT_ANSWER)[-1]
        self._logger.info(f"ask_bot  got  {element.text}")
        return element.text

# if __name__ == '__main__':
#     chatGPT = ChatGPT(update_extension=True)
#     try:
#
#         if chatGPT.authorization():
#             chatGPT.ask_bot("расскажи анекдот")
#         sleep(300)
#     except Exception as ex:
#         print(f"Исключение: {ex} {traceback.print_exc()}")
#         sleep(30)
#
#     finally:
#         chatGPT.finish_work()
