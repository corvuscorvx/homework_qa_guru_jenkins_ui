import os

import pytest
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from utils import attach

from pages.registration_page import RegistrationPage


load_dotenv()


def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        default="chrome",
        choices=("chrome", "firefox"),
        help="Browser to use"
    )
    parser.addoption(
        "--browser_version",
        default="152.0",
        choices=("148.0", "151.0", "152.0", "153.0", "154.0"),
        help="Browser version to use (148.0/151.0/152.0 for Chrome, 153.0/154.0 for Firefox)"
    )
    parser.addoption(
        "--headless",
        choices=["true", "false"],
        default="false",
        help="Launch the browser in headless mode"
    )
    parser.addoption(
        "--window_size",
        default="1920*1080",
        choices=("1280*720", "1366*768", "1920*1080", "2560*1440"),
        help="Window size"
    )
    parser.addoption(
        "--base_url",
        default=os.getenv("BASE_URL"),
        help="Base URL of the site under test"
    )


@pytest.fixture(scope='function')
def setup_browser(request):
    browser = request.config.getoption("--browser")
    browser_version = request.config.getoption("--browser_version")
    headless = request.config.getoption("--headless").lower() == "true"
    window_size = request.config.getoption("--window_size")

    width, height = window_size.split("*")

    if browser == "chrome":
        options = ChromeOptions()
    elif browser == "firefox":
        options = FirefoxOptions()
    else:
        raise pytest.UsageError("Please choose chrome or firefox")

    if headless:
        options.add_argument("--headless")

    selenoid_capabilities = {
        "browserName": browser,
        "browserVersion": browser_version,
        "selenoid:options": {
            "enableVNC": True,
            "enableVideo": True,
            "window": {
                "width": int(width),
                "height": int(height)
            }
        }
    }
    options.capabilities.update(selenoid_capabilities)

    selenoid_url = os.getenv("SELENOID_URL")
    selenoid_login = os.getenv("SELENOID_LOGIN")
    selenoid_password = os.getenv("SELENOID_PASSWORD")

    command_executor = f"https://{selenoid_login}:{selenoid_password}@{selenoid_url}/wd/hub"

    driver = webdriver.Remote(
        command_executor=command_executor,
        options=options
    )

    yield driver

    attach.add_screenshot(driver)
    attach.add_page_source(driver)
    attach.add_console_logs(driver)
    attach.add_video(driver)

    driver.quit()


@pytest.fixture(scope="function")
def registration_page(setup_browser, base_url):
    setup_browser.get(f"{base_url}/one-page-form/automation-practice-form.html")
    return RegistrationPage(setup_browser)


@pytest.fixture
def base_url(request):
    return request.config.getoption("--base_url")


@pytest.fixture(scope="function")
def temp_test_file():
    file_name = "test_image.jpg"
    temp_file_path = os.path.abspath(file_name)
    with open(temp_file_path, "w", encoding="utf-8") as f:
        f.write("fake image data")

    yield temp_file_path, file_name

    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)
