import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selene import Browser, Config
from dotenv import load_dotenv

from utils import attach

from pages.registration_page import RegistrationPage

DEFAULT_BROWSER_VERSION = "128.0"


def pytest_addoption(parser):
    parser.addoption(
        '--browser_version',
        default='128.0'
    )


@pytest.fixture(scope='session', autouse=True)
def load_env():
    load_dotenv()


@pytest.fixture(scope='function')
def setup_browser(request):
    browser_version = request.config.getoption('--browser_version')
    browser_version = browser_version if browser_version != "" else DEFAULT_BROWSER_VERSION

    options = Options()
    selenoid_capabilities = {
        "browserName": "chrome",
        "browserVersion": browser_version,
        "selenoid:options": {
            "enableVNC": True,
            "enableVideo": True
        }
    }
    options.capabilities.update(selenoid_capabilities)

    login = os.getenv('LOGIN')
    password = os.getenv('PASSWORD')

    driver = webdriver.Remote(
        command_executor=f"https://{login}:{password}@selenoid.autotests.cloud/wd/hub",
        options=options
    )
    browser = Browser(Config(driver))

    yield browser

    attach.add_screenshot(browser)
    attach.add_logs(browser)
    attach.add_html(browser)
    attach.add_video(browser)

    browser.quit()


@pytest.fixture(scope="function")
def registration_page(setup_browser):
    driver.get("https://qa-guru.github.io/one-page-form/automation-practice-form.html")
    return RegistrationPage(setup_browser)


@pytest.fixture(scope="function")
def temp_test_file():
    file_name = "test_image.jpg"
    temp_file_path = os.path.abspath(file_name)
    with open(temp_file_path, "w", encoding="utf-8") as f:
        f.write("fake image data")

    yield temp_file_path, file_name

    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)
