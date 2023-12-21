import streamlit as st

import os
import requests

# App title
st.set_page_config(page_title="💬 PaLM 2 Chatbot")

with st.sidebar:
    st.title('💬 PaLM 2 Chatbot')

    st.subheader('Models')
    selected_model = st.sidebar.selectbox('Choose a model', ['PaLM2', 'Gemini'], key='selected_model')
    if selected_model == 'PaLM2':
        url = 'http://127.0.0.1:5000/generate'
    elif selected_model == 'Gemini':
        url = 'http://127.0.0.1:5000/gemini'

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]


st.sidebar.button('Clear Chat History', on_click=clear_chat_history)


# Function for generating LLaMA2 response. Refactored from https://github.com/a16z-infra/llama2-chatbot
def generate_response(prompt_input):
    # url = 'http://127.0.0.1:5000/generate'
    # url = 'http://127.0.0.1:5000/gemini'
    prompts = """Generate code to solve a problem.=>1,
    How does the sorting algorithm work?=>0,
    Create a program that calculates the sum of numbers.=>1,
    What is artificial intelligence?=>0,
    Write a function to find the factorial of a number.=>1,
    Explain the concept of recursion in programming.=>0,
    Implement a basic calculator in Python.=>1,
    Discuss the benefits of using version control in software development.=>0,
    Provide an example of a quicksort algorithm in pseudocode.=>1,
    What is the difference between a list and a tuple in Python?=>0,
    Create a program to check if a given number is prime.=>1,
    Compare and contrast object-oriented programming and procedural programming.=>0,
    How to handle exceptions in Python?=>1,
    Generate code for a simple text-based game in Java.=>1,"""

    prompt_input = prompt_input
    payload = {'prompt': prompt_input, 'temperature': 0.2}
    response = requests.post(url, json=payload)
    result = response.json()

    return result['response']


# User-provided prompt
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)