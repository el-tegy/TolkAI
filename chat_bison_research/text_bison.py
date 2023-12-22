import vertexai
from vertexai.language_models import ChatModel, InputOutputTextPair
from vertexai.preview.language_models import TextGenerationModel

vertexai.init(project="ping38", location="us-central1")
def chat_text_bison(query):
    model = TextGenerationModel.from_pretrained("text-bison@002")
    parameters = {
        "candidate_count": 1,
        "max_output_tokens": 1024,
        "temperature": 0.2,
        "top_p": 0.8,
        "top_k": 40
    }
    context_prompt = """
                     Define the categories for the text below? 
                                - code : if a code is necessary for the response, if the question concern coding, algorithms, script or any software domains.
                                - image : if the question is asking for a guide, steps or how to do something on a dataviz tool like power bi, qlik, etc
                                - text : if a definition (even on power bi, qlik sense) or otherwise
                                No other category is accepted. print directly the category. No other explanation is necessary.
                     """
    prompt = context_prompt + query
    # PaLM2 model

    response = model.predict(
        prompt,
        **parameters,

    )

    return response.text