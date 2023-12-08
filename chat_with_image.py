import os
import requests
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from IPython.display import Image, display
from vertexai.language_models import ChatModel
from IPython.core.display import HTML
import warnings
import re  # Import the 're' module for regular expressions

load_dotenv()

def search_images_on_google(user_query):
    """
    Search for images on Google based on the user query without a restriction.

    Args:
    - user_query (str): The user's query.

    Returns:
    - List of image URLs.
    """
    # site_specific_query = f"{} site:microsoft.com"
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": user_query,
        "cx": "b3cc7e87732c140e9",
        "key": os.getenv("API_KEY"),
        "searchType": "image",
        "num": 5
    }
    response = requests.get(url, params=params)
    data = response.json()

    if 'items' in data:
        items_links = [item['link'] for item in data['items']]
        return items_links
    else:
        print("No results found.")
        return []

def query_from_url(image_url):
    """
    Query a URL using a specific API (e.g., Salesforce's Blip Image Captioning API).

    Args:
    - image_url (str): The URL of the image.

    Returns:
    - JSON response from the API.
    """
    api_url_ = os.getenv("API_URL")
    headers_ = {"Authorization": os.getenv("HEADERS")}
    data = {"url": image_url}
    response = requests.post(api_url_, headers=headers_, json=data)
    return response.json()

def combine_text_and_image(response_text, items_links):
    """
    Combine the chat response with relevant images.

    Args:
    - response_text (str): The text response from the chat model.
    - items_links (list): List of image URLs.

    Returns:
    - Combined text with images.
    """
    
    labels = [label.strip("[]") for label in re.findall(r'\[.*?\]', response_text)]
    
    if labels:
        for label in labels:
            # Search for images corresponding to the label
            images = search_images_on_google(label)
            
            # Display the label in the response
            response_text += f"\n\n[{label}]:\n"
            
            if images:
                # Find the most relevant image for the label using cosine similarity
                most_relevant_image = find_most_relevant_image(label, images, items_links)
                
                # Display the most relevant image
                response_text += f"{most_relevant_image})\n"
        images_for_labels = {}

    return response_text

def find_most_relevant_image(label, images, items_links):
    """
    Find the most relevant image for each label in the chat-bison response if many

    Args :
        - lable(str) : Label of the image retrieved in the chat response
        - images(str) : url link of the images found using google search
        - items_link : all the links of the images found
    
    Return :
        - most relevant image for each label   
    """
    combined_texts = [label] + items_links
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(combined_texts)

    most_relevant_image = None
    highest_similarity = -1

    # Find the most relevant image based on cosine similarity
    for image_url in images:
        tfidf_image = vectorizer.transform([label, image_url])
        similarity = cosine_similarity(tfidf_matrix[0], tfidf_image[1])[0, 0]

        if similarity > highest_similarity:
            highest_similarity = similarity
            most_relevant_image = image_url

    return most_relevant_image

def power_bi_chat(user_query):
    """
    Initiate a chat with the Power BI chat model and enhance the response with relevant images.

    Args:
    - user_query (str): The user's query.
    - temperature (float): The temperature parameter for controlling randomness in token selection.

    Returns:
    - None (prints the combined response).
    """
    chat_model = ChatModel.from_pretrained("chat-bison")

    parameters = {
        "candidate_count": 1,
        "temperature": 0.2,
        "max_output_tokens": 1024,
        "top_p": 0.8,
        "top_k": 40,
    }

    chat = chat_model.start_chat(
        context="Previous messages or context information"
    )

    response = chat.send_message(user_query, **parameters)
    response_text = response.text

    # Call search_images_on_google to get items_links
    items_links = search_images_on_google(user_query)

    response_text = combine_text_and_image(response_text, items_links)

    print(f"Response from Model:\n {response_text}")

if __name__ == "__main__":
    user_query = "How to create a histogram in Power BI step by step and include images for better comprehension of the steps to follow"
    power_bi_chat(user_query)
