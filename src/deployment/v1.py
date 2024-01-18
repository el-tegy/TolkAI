import streamlit as st

import sys
from pathlib import Path

# Add the src directory to sys.path to allow for absolute imports
root_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(root_dir))
from agent.agent import chat_with_agent
from langchain.memory import ConversationBufferMemory
from langchain.memory import StreamlitChatMessageHistory
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
import streamlit as st
from google.oauth2 import service_account
import googleapiclient.discovery


scopes = ['https://www.googleapis.com/auth/cloud-platform']

# Load the service account credentials from Streamlit secrets
creds = service_account.Credentials.from_service_account_info(
    st.secrets["service_account"],
    scopes= scopes
)

# Use the credentials to authenticate your Google Cloud client
service = googleapiclient.discovery.build('aiplatform', 'v1', credentials=creds)


st.set_page_config(page_title="TolkAI")
st.title('TolkAI')



# Set up memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")
memory = ConversationBufferMemory(memory_key="chat_history", chat_memory=msgs)
reset_history = st.sidebar.button("Reset chat history")
if len(msgs.messages) == 0 or reset_history:
    msgs.clear()
    msgs.add_ai_message("Hello my name is TolkAI. How can I help you?")
    st.session_state["last_run"] = None

view_messages = st.expander("View the message contents in session state")
#"st.session_state:", st.session_state.messages

#for msg in st.session_state.messages:
 #   st.chat_message(msg["role"]).write(msg["content"])
for msg in msgs.messages:
    #st.chat_message(msg.type).write(msg.content)
    st.chat_message(msg.type).markdown(msg.content, unsafe_allow_html=True)

if prompt := st.chat_input():
    st.chat_message("human").write(prompt)
    # Note: new messages are saved to history automatically by Langchain during run
    response = chat_with_agent(prompt, "TalkAI", memory)
    #st.chat_message("ai").write(response)
    st.chat_message("ai").markdown(response, unsafe_allow_html=True)

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

