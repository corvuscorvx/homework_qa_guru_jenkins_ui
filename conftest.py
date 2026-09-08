import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from utils import attach

from pages.registration_page import RegistrationPage


@pytest.fixture(scope='function')
def setup_browser():
    options = Options()

    selenoid_capabilities = {
        "browserName": "chrome",
        "browserVersion": "151.0",
        "selenoid:options": {
            "enableVNC": True,
            "enableVideo": True
        }
    }
    options.capabilities.update(selenoid_capabilities)

    driver = webdriver.Remote(
        command_executor="https://user1:1234@selenoid.qa.guru/wd/hub",
        options=options
    )


    yield driver

    attach.add_screenshot(driver)
    attach.add_page_source(driver)
    attach.add_console_logs(driver)
    attach.add_video(driver)

    driver.quit()


@pytest.fixture(scope="function")
def registration_page(setup_browser):
    setup_browser.get("https://qa-guru.github.io/one-page-form/automation-practice-form.html")
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
