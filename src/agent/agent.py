# Import necessary modules and classes
import os
import sys
from pathlib import Path

# Add the src directory to sys.path to allow for absolute imports
root_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(root_dir))
os.chdir(root_dir)
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain_community.utilities.google_search import GoogleSearchAPIWrapper
from langchain.chains import LLMChain
import sys
#sys.path.append('C:/Users/user/ping3/TolkAI/src')
from template.template import CustomPromptTemplate, read_template
from parse.parser import CustomOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAI
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
from utils.config import load_config 
from agent.image_retrieval import image_retrieval_pipeline
from agent.image_retrieval import multiple_query_image_retrieval
from agent.codey import code_generation
from langchain_openai import ChatOpenAI,OpenAI
import google.generativeai as genai
import streamlit as st
from langchain.callbacks.manager import (
    AsyncCallbackManager,
    AsyncCallbackManagerForChainRun,
    CallbackManager,
    CallbackManagerForChainRun,
    Callbacks,
)

# Access API key stored in Streamlit's secrets
google_api_key = st.secrets["api_keys"]["GOOGLE_API_KEY"]
google_cse_id = st.secrets["api_keys"]["GOOGLE_CSE_ID"]
google_genai_api_key = st.secrets["api_keys"]["GOOGLE_GENAI_API_KEY"]
openai_api_key = st.secrets["api_keys"]["OPENAI_API_KEY"]

load_dotenv()
# Load configuration from config.yml
config = load_config()
genai.configure(api_key=google_genai_api_key)

def setup_agent(chatbot_name, memory, callbacks):
    # Instantiate a SerpAPIWrapper object for search functionality
    search = GoogleSearchAPIWrapper(
        google_api_key = google_api_key,
        google_cse_id = google_cse_id,
        k=10
    )
    # Instantiate a datetime object for datetime functionality
    tools = [
        Tool(
        name="Search",
           func=search.run,
           description="Useful when you want to respond to user requests that are related to current events,actuallity, real-time information  or if we don't know the answer"
        ),
        Tool(
            name="Images links from images labels",
           func=image_retrieval_pipeline,
            description="Useful when someone asks an image or  advice on how to accomplish a specific task in data analytics software like Power BI Desktop or Tableau, you can enhance your responses by adding links to images\
                we can also provide an image of an object"
        ),
        Tool(
           name="code from query",
          #  name="General query",
            func=code_generation,
            description="Useful when you want to answer questions or advice related to language of programmation, programs, scrips, code or algorithms."
            #description="Useful when you want to respond to user requests that aren't related to current events or specific tasks in data analytics software.\
             #     The input need to be the original request of the user"
        ),
    ]

    # Set up the prompt template using the base.txt file and the tools list
    prompt = CustomPromptTemplate(
        template=read_template(str(Path(__file__).resolve().parent.parent / "template" / "base.txt")).replace(
            "{chatbot_name}", chatbot_name),
        tools=tools,
        input_variables=["input", "intermediate_steps", "chat_history"]
    )

    # Instantiate a CustomOutputParser object for parsing output
    output_parser = CustomOutputParser()

    # Instantiate a ChatOpenAI object for language model interaction
    llm = ChatGoogleGenerativeAI(model="gemini-pro",
                                google_api_key=google_genai_api_key,
                                temperature=0.1) 

    gpt4 = ChatOpenAI(model="gpt-4-0125-preview", 
                    openai_api_key = openai_api_key,streaming=True
                    )
    
    gpt = ChatOpenAI(model="gpt-3.5-turbo-1106", 
                    openai_api_key = openai_api_key,streaming=True
                    )
    # Set up the LLMChain using the ChatOpenAI object and prompt template
    llm_chain = LLMChain(llm=gpt, prompt=prompt)

    # Extract tool names from the tools list
    tool_names = [tool.name for tool in tools]
    # Set up the LLMSingleActionAgent with LLMChain, output parser, and allowed tools
    agent = LLMSingleActionAgent(
        llm_chain=llm_chain,
        output_parser=output_parser,
        stop=["\nObservation:"],
        allowed_tools=tool_names
    )

    # Create an AgentExecutor from the agent and tools with verbose output
    agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, memory=memory, callbacks=callbacks)
    return agent_executor


def chat_with_agent(user_input: str, chatbot_name: str, memory, callbacks):
    # Set up the agent using the setup_agent() function
    agent_executor = setup_agent(chatbot_name, memory, callbacks=callbacks)
    # Execute the agent with the given user_input and get the responses
    response = agent_executor.run(user_input, callbacks=callbacks)
    # If the response is a dictionary, return the 'output' value, otherwise, return the response itself
    if isinstance(response, dict):
        return response.get("output")
    else:
        return response

"""
if __name__:
    # Load environment variables from .env file
    load_dotenv(config["Key_File"])
    # Get the chatbot name from the config.yml file
    chatbot_name = "TolkAI"
    # Get the user input from the user
    user_input = "Who are you?"
    #user_input = "provide me with a step by step guide on how to create a time series in Power BI. In your answer, \
    #include relevant images showing me where to click in Power BI so that I can easily follow up"
    #user_input = "What is the difference between a bar chart and a line chart?"
    #user_input = "Give me the python code to sum up all the elements in a list."
    #user_input = "Comment créer un diagramme en série temporelle dans Qlik Sense ?"
    # Get the response from the agent
    response = chat_with_agent(user_input, chatbot_name)
    # Print the response
    print(response)"""
