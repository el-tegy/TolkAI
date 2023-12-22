import vertexai
from vertexai.language_models import ChatModel, InputOutputTextPair

#vertexai.init(project="ping38", location="us-central1")
def chat_bison(query):
    chat_model = ChatModel.from_pretrained("chat-bison")
    parameters = {
        "candidate_count": 1,
        "max_output_tokens": 1024,
        "temperature": 0.2,
        "top_p": 0.8,
        "top_k": 40
    }
    chat = chat_model.start_chat(
        context="""
                You're an AI that provides relevant steps and images to solve business intelligence problems if it's necessary.
                You politely answer all kinds of questions based on your knowledge, and problem solving requires steps and images if it's necessary.
                """,
    )
    response = chat.send_message(query, **parameters)
    return response.text
