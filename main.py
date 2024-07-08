# Selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# LLM
from llm import LLMInterface 

# Instantiating the webdriver and connecting it to 2048
driver = webdriver.Chrome()
driver.get("https://play2048.co/")

# Checking that 2048 is the title of the connected webpage
assert "2048" in driver.title

# Waiting for cookies prompt to appear
COOKIE_TIMEOUT = 10

try:
    accept_cookies_button = WebDriverWait(driver, COOKIE_TIMEOUT).until(
        EC.presence_of_element_located((By.ID, "ez-accept-all"))
    )
except:
    print(f"Cookies prompt did not appear within {COOKIE_TIMEOUT} seconds.")
    driver.quit()

# Accepting conditions
accept_cookies_button.click()

# Waiting for the grid to appear
GRID_TIMEOUT = 10

try:
    grid = WebDriverWait(driver, GRID_TIMEOUT).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "game-container"))
    )
except:
    print(f"Grid did not appear within {GRID_TIMEOUT} seconds.")
    driver.quit()

llm_interface = LLMInterface(driver)

# print(llm_interface.ask_llm_with_tools("Press the up arrow key"))
print(llm_interface.ask_llm_with_tools("What's 5 times forty-two"))
# print(llm_interface.ask_llm_with_tools("Fullscreen the window."))