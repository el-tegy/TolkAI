import streamlit as st
import sys
sys.path.append('c/Users/elise/Documents/S9/TolklAI-1/src/agent/agent.py')  # Replace with the actual path
from agent.agent import setup_agent
sys.path.append('c/Users/elise/Documents/S9/TolklAI-1/src/agent/image_retrieval.py')
from agent.image_retrieval import image_retrieval

# Initialize the LangChain agent with OpenAI (or any other model you have)
chatbot_name = 'TolkAI'
agent_executor = setup_agent(chatbot_name)

# Title of the chatbot
st.title('LLM Chatbot')

# Initialize or load the chat history from the session state
if 'chat_histories' not in st.session_state:
    st.session_state.chat_histories = {}

if 'current_chat' not in st.session_state:
    st.session_state.current_chat = []

# Function to name the chat based on the first user prompt
def name_chat(chat):
    if chat:
        # Use the first message as the name or a placeholder if empty
        return chat[0].replace('You: ', '')[:50]  # Limit name to 50 characters
    return "Unnamed Chat"

# Sidebar with chat history
with st.sidebar:
    st.header("Chat Histories")
    # Display chat history names and make them selectable
    chat_names = [name_chat(chat) for chat in st.session_state.chat_histories.values()]
    selected_chat_name = st.radio('Select a chat to view', options=chat_names, index=0)
    # Button to start a new chat
    if st.button('New Chat'):
        # Save current chat to history before starting a new chat
        if st.session_state.current_chat:
            chat_name = name_chat(st.session_state.current_chat)
            st.session_state.chat_histories[chat_name] = st.session_state.current_chat
        st.session_state.current_chat = []

# Function to get response from LangChain agent and update conversation
def get_response():
    if user_input:
        # Add user input to the current chat list
        st.session_state.current_chat.append(f"You: {user_input}")
        # Get the response from the LangChain agent
        #response = langchain_agent.complete(user_input)
        # Execute the agent with the given user_input and get the response
        response = agent_executor.run(user_input)
        # If the response is a dictionary, return the 'output' value, otherwise, return the response itself
        if isinstance(response, dict):
            response = response.get("output")
        # Add the chatbot response to the current chat list
        st.session_state.current_chat.append(f"Bot: {response}")
        # Clear the input box
        st.session_state.user_input = ''

# User input text box
user_input = st.text_input("Type your message here...", key="user_input")

# Button to send the message
send_button = st.button("Send", on_click=get_response)

# Display the current chat or a selected chat from history
if chat_names:
    # If a previous chat is selected, display it
    if selected_chat_name != name_chat(st.session_state.current_chat):
        selected_chat = st.session_state.chat_histories[selected_chat_name]
        for message in selected_chat:
            st.text_area("", message, height=70, key=message + str(selected_chat.index(message)))
else:
    # If no chat is selected, or it's the current chat, display the current chat
    for message in st.session_state.current_chat:
        st.text_area("", message, height=70, key=message + str(st.session_state.current_chat.index(message)))

if __name__ == '__main__':
    st.run()
