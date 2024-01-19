from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
def code_generation(query):
    """
        Generate code from query

        Args:
            query(str) : the query that needs code generation

        Returns:
            str: the answer of the model to the query
    """
    chat = ChatGoogleGenerativeAI(model="codechat-bison",
                            google_api_key="AIzaSyANitOObhh9yTC7Sd6GdiLQGcLJgI1Tz7E",
                            temperature=0.1)
    message = chat.invoke(query)
    return message.content

#print(code_generation("Write a Python function to identify all prime numbers"))
