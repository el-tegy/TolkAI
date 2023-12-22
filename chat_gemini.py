import vertexai
from vertexai.preview.generative_models import GenerativeModel



#This function is responsible for generating the response
def gemini_pro_call(prompt: str, **kwargs) -> str:
    """
    Generate a response based on the prompt using the Gemini Pro model.

    Args:
        prompt (str): The input prompt for the language model.
        **kwargs (Any): Additional keyword arguments.

    Returns:
        str: The generated response by the language model.
    """
    gemini_pro_model = GenerativeModel("gemini-pro")
    model_response = gemini_pro_model.generate_content(
        prompt,
        generation_config={"temperature": 0.1}
    )
    return model_response.candidates[0].content.parts[0].text


#This funtion is responsible for calling the generation function and retrieving the response.
def chat_gemini(query: str) -> str:
    """
    A function to interact with the Gemini Pro language model.

    Args:
        query (str): The user's input/query.

    Returns:
        str: The model's response to the user's input.
    """
    response = gemini_pro_call(query)
    return response
