
import streamlit as st
import sys



sys.path.append('/Users/mnguemnin/Documents/Ping38/untitled folder/TolkAI')

from src.agent.agent import chat_with_agent
from langchain.memory import ConversationBufferMemory
from langchain.memory import StreamlitChatMessageHistory
from langchain.callbacks import StreamlitCallbackHandler




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



