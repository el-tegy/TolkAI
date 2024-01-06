"""

This module use google search to find images of a query, gemini-pro-vision to describe each image
and a cosine similarity to get the relevant image which meet the most with your query

"""
import requests
import random
import pandas as pd
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from vertexai import init as vinit
from vertexai.preview.generative_models import GenerativeModel
from concurrent.futures import ThreadPoolExecutor, as_completed
from embedding_prediction_client import EmbeddingPredictionClient

#from IPython.display import Image, display
PROJECT_ID = 'ping38'
url = "https://www.googleapis.com/customsearch/v1"
total_images = 20 # Total number of images to download
images_per_request = 5  # Maximum number of images per request
params = {
    "cx": "b3cc7e87732c140e9",
    "key": "AIzaSyANitOObhh9yTC7Sd6GdiLQGcLJgI1Tz7E",
    "searchType": "image",
    "num": images_per_request,
    "fileType": "BMP, GIF, JPEG, PNG"
}
client = EmbeddingPredictionClient(project=PROJECT_ID)


def image_search(query):
    all_images = []  # List to hold all the images

    for start_index in range(1, total_images + 1, images_per_request):
        response = requests.get(url, params=params)
        data = response.json()
        params["q"] = query
        params["start"] = start_index
        if 'items' in data:
            all_images.extend(item['link'] for item in data['items'])
        else:
            pass
    return all_images

def get_timestamp():
    return str(datetime.now().strftime(("%Y-%m-%d-%H-%M-%S")))

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
        [image_link, """Give me a very brief description of this image"""],
        generation_config={
            "max_output_tokens": 1024,
            "temperature": 0.4,
            "top_p": 1,
            "top_k": 32
        },
    stream=True,
    )
    return " ".join([response.candidates[0].content.parts[0].text for response in responses])

# Function to apply captioning to a list of image URLs using multiple threads
def image_captioning_parallel(items_links):
    captions = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(generate, url): url for url in items_links}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                caption = future.result()
            except:
                pass
            else:
                captions[url] = caption
    return captions

def getTextEmbedding(client, text):
    response = client.get_embedding(text=text, image_bytes=None)
    return response.text_embedding

def image_selection(query, client, data):
    """
    Research of the relevant images

    Args:
        query (str): The initial query we are looking for an image
        data (pd.DataFrame): DataFrame which contains description of each image

    Returns:
        str: A link of the relevant image
    """
    # Get the embedding for the query text
    query_vect = getTextEmbedding(client, query)
    query_vect = np.array(query_vect).reshape(1, -1)  # Reshape to 2D array

    # Get embeddings for each caption and compute cosine similarity
    data['embedding'] = data['Caption'].apply(lambda x: getTextEmbedding(client, x))
    data['cos_sim'] = data['embedding'].apply(lambda x: cosine_similarity(query_vect, np.array(x).reshape(1, -1))[0][0])

    # Sort by cosine similarity in descending order and get the most relevant item
    most_relevant_item = data.sort_values(by='cos_sim', ascending=False).iloc[0]

    return most_relevant_item['ImageURL']

def image_retrieval_pipeline(query):
    images = image_search(query)
    random.shuffle(images)
    captions = image_captioning_parallel(images[:10])
    df_items = pd.DataFrame(list(captions.items()), columns=['ImageURL', 'Caption'])
    try: 
        return image_selection(query, client, df_items)
    except:
        return df_items[0]['ImageURL']