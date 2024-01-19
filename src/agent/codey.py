from langchain.chat_models import ChatVertexAI
from langchain.prompts import ChatPromptTemplate
import google.generativeai as genai
import streamlit as st


# Access API key stored in Streamlit's secrets
google_api_key = st.secrets["api_keys"]["GOOGLE_GENAI_API_KEY"]

genai.configure(api_key=google_api_key)
def code_generation(query):
    """
        Generate code from query

        Args:
            query(str) : the query that needs code generation

        Returns:
            str: the answer of the model to the query
    """
    chat = ChatVertexAI(
        model_name="codechat-bison", max_output_tokens=2500, temperature=0.1
    )
    message = chat.invoke(query)
    return message.content

#print(code_generation("Write a Python function to identify all prime numbers"))
