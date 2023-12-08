import vertexai
from vertexai.language_models import ChatModel, InputOutputTextPair

#vertexai.init(project="ping38", location="us-central1")
chat_model = ChatModel.from_pretrained("chat-bison")
parameters = {
    "candidate_count": 1,
    "max_output_tokens": 1024,
    "temperature": 0.2,
    "top_p": 0.8,
    "top_k": 40
}
chat = chat_model.start_chat(
    context="""""",
)
response = chat.send_message("""\"Provide me with a step by step guide to create a heat map chart in Power BI Desktop (include images in each step of the guide so that I can easily follow up)\"""", **parameters)
print(f"Response from Model: {response.text}")