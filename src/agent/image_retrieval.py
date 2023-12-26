"""

This module use google search to find images of a query, gemini-pro-vision to describe each image
and a cosine similarity to get the relevant image which meet the most with your query

"""
import os
from dotenv import load_dotenv
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from vertexai.preview.generative_models import GenerativeModel, Part
#from IPython.display import Image, display
url = "https://www.googleapis.com/customsearch/v1"
total_images = 30 # Total number of images to download
images_per_request = 10  # Maximum number of images per request

load_dotenv()

def image_search(query):
    all_images = []  # List to hold all the images

    for start_index in range(1, total_images + 1, images_per_request):
        params = {
            "q": query,
            "cx": os.getenv("Google_CSE_ID"),
            "key": os.getenv("Google_API_Key"),
            "searchType": "image",
            "num": images_per_request,
            "start": start_index,
            "fileType": "BMP, GIF, JPEG, PNG"
        }
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'items' in data:
             all_images.extend(data['items'])
        else:
            print('an error occured while searching')
    return all_images


def generate(image_link):
    """
    Description of the images 

    Args:
        image_link (str): link of the image

    Returns:
        str: A complete description of the images link
    """
    model = GenerativeModel("gemini-pro-vision")
    responses = model.generate_content(
        [image_link, """Give me a brief description of this image"""],
        generation_config={
            "max_output_tokens": 1024,
            "temperature": 0.4,
            "top_p": 1,
            "top_k": 32
        },
    stream=True,
    )
    result=""
    for response in responses:
        result+=response.candidates[0].content.parts[0].text
    return result  


def image_captioning(list_of_items):
    """
    Gathering the description of images 

    Args:
        list_of_items (list): list of images found by google search

    Returns:
        list: a list which contains the description of each image
    """
    combined_texts=[]
    items=list_of_items
    items_links=[item['link'] for item in items]
    for item in items_links:
        try:
            output = generate(item)
            resume = output
            #print(f"{item}")
            combined_texts.append(resume)
            #combined_texts.insert(0, user_query)
            return combined_texts
        except Exception as e:
            return e

def image_selection(list_of_combined_texts, items, query):
    """
    Resaech of the relevant images

    Args:
        list_of_combined_texts (list): list which conatins description of each image
        items (list):list of images
        query(str) : the initial query we are looking for an image

    Returns:
        str: A link of the relevant image
    """
    combined_texts=list_of_combined_texts
    combined_texts.insert(0, query)
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(combined_texts)
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
    most_similar_idx = cosine_similarities.argsort()[0][-1]
    most_relevant_item = items[most_similar_idx]
    return most_relevant_item['link']

def image_retrieval_pipeline(image_label):
    """
    Research the relevant image of a label

    Args:
        image_label(str) : the label of images provide by Palm2

    Returns:
        str: A link of the relevant image
    """
    items = image_search(image_label)
    combined_texts = image_captioning(items)
    image_link = image_selection(combined_texts, items, image_label)
    return image_link
