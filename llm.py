import os

# LangChain
from langchain_openai import AzureChatOpenAI
from langchain_core.messages.base import BaseMessage
from langchain_core.tools import tool 

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
        print("[INFO] Instantiating the LLM...")
        llm = AzureChatOpenAI(
            azure_deployment="gpt-4o",
            api_version="2024-05-01-preview",
            temperature=0
        )

        self.llm = llm
        self.driver = driver

        # Adding the tools to the LLM's toolkit
        print("[INFO] Generating tools...")
        tools = generate_tools_for_webdriver(self.driver)

        print("[INFO] Binding tools...")
        self.llm_with_tools = self.llm.bind_tools(tools)

        print("[INFO] Initiation Complete!")

    def say_hello(self) -> BaseMessage:
        return self.llm.invoke("Hello")
        
    def ask_llm_with_tools(self, query: str) -> BaseMessage:
        msg = self.llm_with_tools.invoke(query)
        
        # If there are any invalid tool calls we print them
        if len(msg.invalid_tool_calls) > 0:
            print("[WARNING] Invalid tool calls occurred:")
            print(msg.invalid_tool_calls)

        return msg