# Import necessary modules and classes
import os
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.utilities import SerpAPIWrapper
from langchain_community.utilities.google_search import GoogleSearchAPIWrapper
from langchain.chains import LLMChain
from template.template import CustomPromptTemplate, read_template
from langchain_google_genai import ChatGoogleGenerativeAI
from parser.parser import CustomOutputParser
from dotenv import load_dotenv
from pathlib import Path
from utils.config import load_config
from image_retrieval import image_retrieval_pipeline
from codey import code_generation

load_dotenv()
# Load configuration from config.yml
config = load_config()

def setup_agent(chatbot_name):
    # Instantiate a SerpAPIWrapper object for search functionality
    #search = GoogleSearchAPIWrapper(
    #    google_api_key = os.getenv("Google_API_Key"),
    #    google_cse_id = os.getenv("Google_CSE_ID"),
    #    k=10
    #)
    # Instantiate a datetime object for datetime functionality
    tools = [
        # Tool(
        #    name="Search",
        #    func=search.run,
        #    description="The Search tool uses Google Search API to conduct Google searches. It retrieves raw search results without any inherent interpretation. \
        #    Utilize this tool only and only when you need to fetch new information on the Internet that you don't know already."
        # ),
        Tool(
            name="Image link from image label",
            func=image_retrieval_pipeline,
            description="This tool returns a image link given an image label passed as a parameter. \
                Utilize this tool to fetch links of images you need to enhance your answer, by passing it images labels \
                such as 'Image of the 'get data' button in Power BI'."
        ),
        Tool(
            name="code from query",
            func=code_generation,
            description="This tool returns a code from a query that necessitates code generation. \
                Utilize this tool to answer questions that ask for programs, scrips, code or algorithms."
        ),
    ]

    # Set up the prompt template using the base.txt file and the tools list
    prompt = CustomPromptTemplate(
        template=read_template(str(Path(__file__).resolve().parent.parent / "template" / "base.txt")).replace(
            "{chatbot_name}", chatbot_name),
        tools=tools,
        input_variables=["input", "intermediate_steps"]
    )

    # Instantiate a CustomOutputParser object for parsing output
    output_parser = CustomOutputParser()

    # Instantiate a ChatOpenAI object for language model interaction
    llm = ChatGoogleGenerativeAI(model="gemini-pro", 
                                google_api_key="AIzaSyANitOObhh9yTC7Sd6GdiLQGcLJgI1Tz7E",
                                temperature=0.1)

    # Set up the LLMChain using the ChatOpenAI object and prompt template
    llm_chain = LLMChain(llm=llm, prompt=prompt)

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
    agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True)
    return agent_executor


def chat_with_agent(user_input: str, chatbot_name: str):
    # Set up the agent using the setup_agent() function
    agent_executor = setup_agent(chatbot_name)
    # Execute the agent with the given user_input and get the response
    response = agent_executor.run(user_input)
    # If the response is a dictionary, return the 'output' value, otherwise, return the response itself
    if isinstance(response, dict):
        return response.get("output")
    else:
        return response


if __name__:
    # Load environment variables from .env file
    load_dotenv(config["Key_File"])
    # Get the chatbot name from the config.yml file
    chatbot_name = "TolkAI"
    # Get the user input from the user
    #user_input = "Who are you?"
    #user_input = "Who is Elisée Tegue?"
    #user_input = "provide me with a step by step guide on how to create a heatmap in Tableau. In your answer, \
    #include relevant images showing me where to click in Power BI so that I can easily follow up"
    #user_input = "What is the difference between a bar chart and a line chart?"
    user_input = "Give me the python code to sum up all the elements in a list."
    #user_input = "Comment créer un diagramme en série temporelle dans Qlik Sense ?"
    # Get the response from the agent
    response = chat_with_agent(user_input, chatbot_name)
    # Print the response
    print(response)