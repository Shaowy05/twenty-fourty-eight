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

# LangChain
from langchain_openai import AzureChatOpenAI
from langchain_core.messages.base import BaseMessage
from langchain_core.tools import tool 
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.output_parsers import StrOutputParser

# LangChain Custom Tools
from tools import generate_tools_for_webdriver

# Selenium
from selenium.webdriver.chrome.webdriver import WebDriver

# Setting up environment variables
os.environ["AZURE_OPENAI_API_KEY"] = "a76ee46fdc07415c90c882417f9757fb"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://cog-oai-openai01-eastus-01.openai.azure.com/"

class LLMInterface:
    def __init__(self, driver: WebDriver) -> None:

        # Instantiating the LLM
        logger.info("Instantiating the LLM...")
        llm = AzureChatOpenAI(
            azure_deployment="gpt-4o",
            api_version="2024-05-01-preview",
            temperature=0
        )

        self.llm = llm
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

        logger.info("Instantiation Complete!")

    def generate_tool_dict(self) -> dict:
        tool_dict = dict()
        for tool in self.tools:
            tool_dict[tool.name] = tool
        
        return tool_dict

    def say_hello(self) -> BaseMessage:
        return self.llm.invoke("Hello")
        
    def ask_llm_with_tools(self, query: str) -> List[BaseMessage]:
        messages = [HumanMessage(query)]

        msg = self.llm_with_tools.invoke(messages)

        # If there are any invalid tool calls we print them
        if len(msg.invalid_tool_calls) > 0:
            logger.warning("Invalid tool calls occurred:")
            print(msg.invalid_tool_calls)

        messages.append(msg) 

        for tool_call in msg.tool_calls:
            selected_tool = self.tool_dict[tool_call["name"].lower()]
            tool_output = selected_tool.invoke(tool_call["args"])
            messages.append(ToolMessage(tool_output, tool_call_id=tool_call["id"]))

        return self.llm_with_tools.invoke(messages) 