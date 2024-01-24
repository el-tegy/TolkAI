import streamlit as st
import os
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.utilities import SerpAPIWrapper
from langchain_community.utilities.google_search import GoogleSearchAPIWrapper
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
import sys
sys.path.append('/Users/mnguemnin/Documents/TolkAI-1/src')
from template.template import CustomPromptTemplate, read_template
from langchain_google_genai import ChatGoogleGenerativeAI
from parser.parser import CustomOutputParser
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
from utils.config import load_config
#from image_retrieval import image_retrieval_pipeline
from image_retrieval_gemini import image_retrieval_pipeline
from codey import code_generation
from langchain.memory import StreamlitChatMessageHistory
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.utilities import SerpAPIWrapper
from langchain_community.utilities.google_search import GoogleSearchAPIWrapper
from langchain.chains import LLMChain
import sys
sys.path.append('/Users/mnguemnin/Documents/TolkAI-1/src')
from template.template import CustomPromptTemplate, read_template
from langchain_google_genai import ChatGoogleGenerativeAI
from parser.parser import CustomOutputParser
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
from utils.config import load_config
#from image_retrieval import image_retrieval_pipeline
from image_retrieval_gemini import image_retrieval_pipeline
from codey import code_generation
import streamlit as st

load_dotenv()
# Load configuration from config.yml
config = load_config()

def setup_agent(chatbot_name, memory):
    # Instantiate a SerpAPIWrapper object for search functionality
    search = GoogleSearchAPIWrapper(
        google_api_key = os.getenv("Google_API_Key"),
        google_cse_id = os.getenv("Google_CSE_ID"),
        k=10
    )
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
        input_variables=["input", "intermediate_steps", "chat_history"]
    )

    print(f"memory{memory}")

    # Instantiate a CustomOutputParser object for parsing output
    output_parser = CustomOutputParser()

    # Instantiate a ChatOpenAI object for language model interaction
    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key="AIzaSyANitOObhh9yTC7Sd6GdiLQGcLJgI1Tz7E")

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

    msgs1 = StreamlitChatMessageHistory()
    memory1 = ConversationBufferMemory(chat_memory=msgs1, return_messages=True, memory_key="chat_history", output_key="output")



    # Create an AgentExecutor from the agent and tools with verbose output
    agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, memory=memory)
    print(f'prompt{prompt}')
    print(f'prompt{agent_executor}')

    return agent_executor


def chat_with_agent(user_input: str, chatbot_name: str, memory, callbacks):
    # Set up the agent using the setup_agent() function
    agent_executor = setup_agent(chatbot_name, memory)
    # Execute the agent with the given user_input and get the response
    response = agent_executor.run(user_input)
    # If the response is a dictionary, return the 'output' value, otherwise, return the response itself
    if isinstance(response, dict):
        return response.get("output")
    else:
        return response


st.set_page_config(page_title="🦜🔗 Demo App")
st.title('🦜🔗 Demo App')

st.title("💬 Travel Assistant")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hi my name is Miles and I am your travel assistant, how can I help you?"}]

# Set up memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")
memory = ConversationBufferMemory(memory_key="chat_history", chat_memory=msgs)
reset_history = st.sidebar.button("Reset chat history")
if len(msgs.messages) == 0 or reset_history:
    msgs.clear()
    msgs.add_ai_message("How can I help you?")
    st.session_state["last_run"] = None
"""if len(msgs.messages) == 0 or st.sidebar.button("Reset chat history"):
    msgs.clear()
    msgs.add_ai_message("How can I help you?")
    st.session_state.steps = {}"""

view_messages = st.expander("View the message contents in session state")
#"st.session_state:", st.session_state.messages

#for msg in st.session_state.messages:
 #   st.chat_message(msg["role"]).write(msg["content"])
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

if prompt := st.chat_input():
    st.chat_message("human").write(prompt)

    # Note: new messages are saved to history automatically by Langchain during run
    response = chat_with_agent(prompt, "TalkAI", memory)
    st.chat_message("ai").write(response)


    # Draw the messages at the end, so newly generated ones show up immediately
with view_messages:
        """
        Memory initialized with:
        ```python
        msgs = StreamlitChatMessageHistory(key="langchain_messages")
        memory = ConversationBufferMemory(chat_memory=msgs)
        ```

        Contents of `st.session_state.langchain_messages`:
        """
        view_messages.json(st.session_state.langchain_messages)