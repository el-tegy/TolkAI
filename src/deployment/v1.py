import streamlit as st
from langchain.callbacks import StreamlitCallbackHandler
import sys
from pathlib import Path
import os
# Add the src directory to sys.path to allow for absolute imports
root_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(root_dir))
#sys.path.append('C:/Users/user/ping3/TolkAI/src')
from agent.agent import chat_with_agent
from langchain.memory import ConversationBufferMemory
from langchain.memory import StreamlitChatMessageHistory
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
import streamlit as st
from google.oauth2 import service_account
import googleapiclient.discovery
import google.auth
import vertexai
from google.cloud import aiplatform

vertexai.init(project="ping38", location="us-west4")

# Retrieve the JSON key file path from Streamlit Secrets
key_path = st.secrets["service_account"]

# Authenticate using the key file
credentials, project_id = google.auth.default()

st.set_page_config(page_title="TolkAI")
st.title('TolkAI')



# Set up memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")
print(msgs)
memory = ConversationBufferMemory(memory_key="chat_history", chat_memory=msgs)
reset_history = st.sidebar.button("Reset chat history")
if len(msgs.messages) == 0 or reset_history:
    msgs.clear()
    msgs.add_ai_message("Bonjour, je suis TolkAI. Comment puis-je vous aider aujourd'hui ?")
    st.session_state["last_run"] = None


for msg in msgs.messages:

    st.chat_message(msg.type).markdown(msg.content, unsafe_allow_html=True)





output_container = st.empty()
if prompt := st.chat_input():

    st.chat_message("human").write(prompt)
    placeholder = st.empty()
    with placeholder.container():
        with st.chat_message("assistant"):
            st_callback = StreamlitCallbackHandler(st.container())
            response = chat_with_agent(prompt, "TolkAI", memory, [st_callback])

            st.container().empty()
            st.markdown(response, unsafe_allow_html=True)

        st.chat_message("assistant").empty()
    placeholder.empty()


    st.chat_message("ai").markdown(response, unsafe_allow_html=True)
