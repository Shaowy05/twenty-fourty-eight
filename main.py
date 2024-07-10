# JSON formatting
import json

# Logging
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="2048.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

file_handler = logging.FileHandler(
    "2048.log",
    mode="w"
)

selenium_logger = logging.getLogger("selenium")
selenium_logger.setLevel(logging.DEBUG)

# Selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# LLM
from llm import LLMInterface 

# Instantiating the webdriver and connecting it to 2048
# selenium_logger = logging.getLogger("selenium").setLevel(logging.DEBUG)
logger.info("Retrieving the Chrome webdriver...")
driver = webdriver.Chrome()
logger.info("Chrome webdriver retrieved")

logger.info("Connecting to 'https://play2048.co/'...")
driver.get("https://play2048.co/")
logger.info("Connected to 'https://play2048.co/'")

# Checking that 2048 is the title of the connected webpage
assert "2048" in driver.title

# Waiting for cookies prompt to appear
COOKIE_TIMEOUT = 10

logger.info("Waiting for cookies to appear...")
try:
    accept_cookies_button = WebDriverWait(driver, COOKIE_TIMEOUT).until(
        EC.presence_of_element_located((By.ID, "ez-accept-all"))
    )
except:
    print(f"Cookies prompt did not appear within {COOKIE_TIMEOUT} seconds.")
    driver.quit()

# Accepting conditions
logger.info("Accepting cookies...")
accept_cookies_button.click()
logger.info("Cookies accepted")

# Waiting for the grid to appear
GRID_TIMEOUT = 10

logger.info("Waiting for 2048 grid to appear...")
try:
    grid = WebDriverWait(driver, GRID_TIMEOUT).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "game-container"))
    )
except:
    print(f"Grid did not appear within {GRID_TIMEOUT} seconds.")
    driver.quit()

# Creating the interface for the LLM
llm_interface = LLMInterface(driver)

# print(llm_interface.ask_llm_with_tools("Press the up arrow key"))
# print(llm_interface.ask_agent("What's 5 times forty-two"))
# print(llm_interface.ask_llm_with_tools("Fullscreen the window."))
# print(llm_interface.ask_llm_with_tools("Say hello"))
# llm_interface.ask_agent("what's 5 * forty-two")

llm_interface.solve()