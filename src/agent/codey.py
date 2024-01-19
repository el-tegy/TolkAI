from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
import google.generativeai as genai
import streamlit as st

# Access API key stored in Streamlit's secrets
google_genai_api_key = st.secrets["api_keys"]["GOOGLE_GENAI_API_KEY"]
genai.configure(api_key=google_genai_api_key)
def code_generation(query):
    """
        Generate code from query

        Args:
            query(str) : the query that needs code generation

        Returns:
            str: the answer of the model to the query
    """
    chat = ChatGoogleGenerativeAI(model="gemini-pro",
                            google_api_key=google_genai_api_key,
                            temperature=0.1)
    message = chat.invoke(query)
    return message.content

#print(code_generation("Write a Python function to identify all prime numbers"))
