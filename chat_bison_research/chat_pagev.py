import re
import vertexai
from image_retrieval import image_retrieval_pipeline
from chat_bison import chat_bison
from vertexai.preview.generative_models import GenerativeModel
import concurrent.futures

vertexai.init(project="ping38", location="us-central1")
def get_chat_bison_output(query):
    doc_text = chat_bison(query)
    return doc_text

def extract_image_labels(text):
    image_labels = re.findall(r'\[Image of the (.*?)\]', text)
    original_labels = ['Image of the ' + item for item in image_labels]
    return original_labels

def enhance_image_labels(image_labels):
    enhanced_labels = []
    for label in image_labels:
        if "Power BI Desktop" not in label:
            label = label + "in Power BI Desktop"
            enhanced_labels.append(label)
        else:
            enhanced_labels.append(label)
    return enhanced_labels

def insert_image_links_parallel(doc_text, image_labels):
    enhanced_labels = enhance_image_labels(image_labels)
    image_links = []

    # Define a function to retrieve image links in parallel
    def retrieve_image_link(label):
        return image_retrieval_pipeline(label)

    # Use ThreadPoolExecutor for parallel processing
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Retrieve image links concurrently
        image_links = list(executor.map(retrieve_image_link, enhanced_labels))

    # Replace image labels with image links in doc_text
    for i, link in enumerate(image_links):
        doc_text = doc_text.replace(f"[{image_labels[i]}]", f'<br><img src={link} width="400">', 1)

    return doc_text


def chat_with_gemini(message):
    #vertexai.init(project="PROJECT_ID", location="us-central1")
    model = GenerativeModel("gemini-pro")
    chat = model.start_chat()
    response = chat.send_message(message)
    return response.text

def mapping(doc_text):
    query = "Here is a text containing steps and images labels. Each image label matches a particular point in a step. I want you to put the right image label below the right point in the right step." + doc_text
    response = chat_with_gemini(query)
    return response

def chat_pagev(query):
    doc_text = get_chat_bison_output(query)
    doc_text = mapping(doc_text)
    image_labels = extract_image_labels(doc_text)
    updated_doc_text = insert_image_links_parallel(doc_text, image_labels)

    return updated_doc_text

#user_query = "How to create a bar chart in Power BI? provide me steps and images"
#print(chat_pagev(user_query))