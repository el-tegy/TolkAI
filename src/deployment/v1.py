import streamlit as st
import time
import streamlit as st
import sys

import sys



sys.path.append('/Users/mnguemnin/Documents/Ping38/untitled folder/TolkAI')

from src.agent.agent import chat_with_agent
#from agent.agent import chat_with_agent
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper, SQLDatabase
from langchain_core.runnables import RunnableConfig
from langchain.memory import ConversationBufferMemory
from langchain.memory import StreamlitChatMessageHistory
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.callbacks import StreamlitCallbackHandler
from langchain_google_genai import ChatGoogleGenerativeAI



st.set_page_config(page_title="TalkAI", layout="wide", initial_sidebar_state="collapsed")

st.title('TalkAI')



# Set up memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")
print(msgs)
memory = ConversationBufferMemory(memory_key="chat_history", chat_memory=msgs)
reset_history = st.sidebar.button("Reset chat history")
if len(msgs.messages) == 0 or reset_history:
    msgs.clear()
    msgs.add_ai_message("Hello my name is TalkAI. How can I help you?")
    st.session_state["last_run"] = None

view_messages = st.expander("View the message contents in session state")
#"st.session_state:", st.session_state.messages

#for msg in st.session_state.messages:
 #   st.chat_message(msg["role"]).write(msg["content"])
for msg in msgs.messages:
    #st.chat_message(msg.type).write(msg.content)
    st.chat_message(msg.type).markdown(msg.content, unsafe_allow_html=True)





output_container = st.empty()
if prompt := st.chat_input():
    #output_container = output_container.container()
    #output_container.chat_message("user").write(prompt)
    #response = chat_with_agent(prompt, "TalkAI", memory)
    #answer_words = response.split()
    #answer_container = output_container.chat_message("assistant", avatar="🦜")

    # Split the answer into words

    # Display each word sequentially
    #for word in answer_words:
    #    answer_container.write(word)
    #    st.empty()  # Optional: Adds a space between words for better readability

   # with st.spinner('Thinking...'):
    #    st.balloons()
    #    st.chat_message("human").write(prompt)
        # Note: new messages are saved to history automatically by Langchain during run
      #  response = chat_with_agent(prompt, "TalkAI", memory)
        # st.chat_message("ai").write(response)
     #   st.chat_message("ai").markdown(response, unsafe_allow_html=True)
        # st.status.update(label="Download complete!", state="complete", expanded=False)
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

        #with st.status(st.chat_message("human").write(prompt)):
            #st_callback = StreamlitCallbackHandler(st.container())

          # Note: new messages are saved to history automatically by Langchain during run
            #response = chat_with_agent(prompt, "TolkAI", memory, [st_callback])

    st.chat_message("ai").markdown(response, unsafe_allow_html=True)
            #st.chat_message("ai").markdown(response, unsafe_allow_html=True)
            # st.status.update(label="Download complete!", state="complete", expanded=False)


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