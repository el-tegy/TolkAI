from langchain.chat_models import ChatVertexAI
from langchain.prompts import ChatPromptTemplate
def code_generation(query):
    """
        Generate code from query

        Args:
            query(str) : the query that needs code generation

        Returns:
            str: the answer of the model to the query
    """
    chat = ChatVertexAI(
        model_name="codechat-bison", max_output_tokens=1000, temperature=0.5
    )

    message = chat.invoke(query)
    return message.content

#print(code_generation("Write a Python function to identify all prime numbers"))