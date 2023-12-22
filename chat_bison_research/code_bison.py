import vertexai
from vertexai.language_models import CodeGenerationModel

vertexai.init(project="ping38", location="europe-west1")
def chat_code_bison(query):
    code_generation_model = CodeGenerationModel.from_pretrained("code-bison@002")
    parameters = {
        "candidate_count": 1,
        "max_output_tokens": 2048,
        "temperature": 0.1,
    }
    response = code_generation_model.predict(query, **parameters)
    return response.text
