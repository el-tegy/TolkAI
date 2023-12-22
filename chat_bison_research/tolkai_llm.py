from text_bison import chat_text_bison
from code_bison import chat_code_bison
from chat_gemini import chat_gemini
from chat_pagev import chat_pagev

def chat_tolkai(query):
    destination = chat_text_bison(query).strip()
    if destination == "image":
        return chat_pagev(query)
    elif destination == "text":
        return chat_gemini(query)
    elif destination == "code":
        return chat_code_bison(query)
    else:
        return "Sorry but I don't understand your question. Can you please rephrase it?"
    