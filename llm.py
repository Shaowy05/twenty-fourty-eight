import os

# Types
from typing import List

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

# Pillow
from PIL import Image

# Image Encoding
import base64

# LangChain
from langchain_openai import AzureChatOpenAI

from langchain_core.messages.base import BaseMessage
from langchain_core.tools import tool 
from langchain_core.messages import HumanMessage, ToolMessage 

# LangGraph
from langgraph.prebuilt import create_react_agent

# LangChain Custom Tools
from tools import generate_tools_for_webdriver

# Selenium
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Setting up environment variables
os.environ["AZURE_OPENAI_API_KEY"] = "a76ee46fdc07415c90c882417f9757fb"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://cog-oai-openai01-eastus-01.openai.azure.com/"

class LLMInterface:
    def __init__(self, driver: WebDriver) -> None:

        # Instantiating the LLM
        logger.info("Instantiating the LLM...")
        self.llm = AzureChatOpenAI(
            azure_deployment="gpt-4o",
            api_version="2024-05-01-preview",
            temperature=0
        )
        logger.info("LLM instantiated")

        self.driver = driver

        # Adding the tools to the LLM's toolkit
        logger.info("Generating tools...")
        self.tools = generate_tools_for_webdriver(self.driver)
        logger.info("Tools successfully generated")

        # Creating a tools dictionary, used to allow the LLM to
        # select the tools using the name of the method.
        logger.info("Generating tools dictionary...")
        self.tool_dict = self.generate_tool_dict()
        logger.info("Tools dictionary successfully generated")

        # Binding the tools to the LLM
        logger.info("Binding tools...")
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        logger.info("Tools bound to LLM")

        # Creating the agent
        # self.agent_executor = create_react_agent(self.llm, self.tools)

        logger.info("Instantiation Complete!")

    def generate_tool_dict(self) -> dict:
        tool_dict = dict()
        for tool in self.tools:
            tool_dict[tool.name] = tool
        
        return tool_dict
        
    def ask_agent(self, query: str) -> List[BaseMessage]:
        messages = [HumanMessage(query)]

        # response = self.agent_executor.invoke({
        #     "messages": messages
        # })

        # If there are any invalid tool calls we print them
        # if len(msg.invalid_tool_calls) > 0:
        #     logger.warning("Invalid tool calls occurred:")
        #     print(msg.invalid_tool_calls)

        # messages.append(msg) 

        # for tool_call in msg.tool_calls:
        #     selected_tool = self.tool_dict[tool_call["name"].lower()]
        #     tool_output = selected_tool.invoke(tool_call["args"])
        #     messages.append(ToolMessage(tool_output, tool_call_id=tool_call["id"]))

        # return self.llm_with_tools.invoke(messages) 

        for chunk in self.agent_executor.stream({"messages": messages}):
            print(chunk)
            print("---------")

        return

    def solve(self):
        # Chain:
        # 1. Get image of current grid
        # 2. Input image into LLM
        # 3. LLM decides which direction to press
        # 4. Presses relevant input
        # 5. Wait for grid to change
        # 6. Inspect the grid:
        #    - If there is 2048 then quit
        #    - Otherwise repeat chain

        logger.info("Entering solve loop...")
        solved = False
        iteration = 1
        while not solved:
            logger.info(f"Starting iteration {iteration}...")

            logger.info("Waiting for grid element...")
            GRID_TIMEOUT = 10
            try:
                grid_elements = WebDriverWait(self.driver, GRID_TIMEOUT).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "game-container"))
                )
            except:
                print(f"Grid did not appear within {GRID_TIMEOUT} seconds.")
                raise Exception
            logger.info("Grid element appeared")

            if len(grid_elements) == 0:
                logger.error("No element with class name 'grid-container'")
                raise Exception

            if len(grid_elements) != 1:
                logger.warning("More than one element with class name 'grid-container'")

            grid = grid_elements[0] 
            logger.info("Taking a screenshot of the grid...")
            grid.screenshot("grid.png")
            logger.info("Screenshot of grid taken.")

            logger.info("Encoding image into base 64...")
            with open("grid.png", "rb") as f:
                grid_image_data = base64.b64encode(f.read()).decode("utf-8")
            logger.info("Image encoded")

            messages = [
                HumanMessage(content=[
                    {
                        "type": "text",
                        "text": "Inspect this image and press a direction key to try and solve the puzzle"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{grid_image_data}"
                        }
                    }
                ])
            ]

            msg = self.llm_with_tools.invoke(messages)

            messages.append(msg)

            for tool_call in msg.tool_calls:
                selected_tool = self.tool_dict[tool_call["name"].lower()]
                tool_output = selected_tool.invoke(tool_call["args"])
                messages.append(ToolMessage(
                    tool_output,
                    tool_call_id=tool_call["id"]
                ))

            iteration += 1

        return