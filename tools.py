from typing import List

from langchain.tools import tool, BaseTool

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys 

def generate_tools_for_webdriver(driver: WebDriver) -> List[BaseTool]:
    """Generate a set of tools that have a webdriver associated with them.""" 

    @tool
    def fullscreen_window() -> None:
        """Tests the drivers functionality"""
        driver.fullscreen_window()

    @tool
    def press_direction(direction: str) -> str:
        """Presses the key given by the direction."""
        action_chain = ActionChains(driver)

        match direction:
            case "up":
                action_chain.send_keys(Keys.UP)
            case "down":
                action_chain.send_keys(Keys.DOWN)
            case "left":
                action_chain.send_keys(Keys.LEFT)
            case "right":
                action_chain.send_keys(Keys.RIGHT)
            case _:
                raise Exception("Invalid direction passed into function.")

        action_chain.perform()
        return "Hello"

    # Multiply Tool - Used for testing
    @tool
    def multiply(first_int: int, second_int: int) -> int:
        """Multipy two integers together."""
        return first_int * second_int 

    return [fullscreen_window, press_direction, multiply] 