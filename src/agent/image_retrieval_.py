"""

This module use google search to find images of a query, gemini-pro-vision to describe each image
and a cosine similarity to get the relevant image which meet the most with your query

"""
import os
from dotenv import load_dotenv
import requests
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from vertexai.preview.generative_models import GenerativeModel
from concurrent.futures import ThreadPoolExecutor, as_completed , wait
from embedding_prediction_client import EmbeddingPredictionClient

load_dotenv()
#from IPython.display import Image, display
PROJECT_ID = 'ping38'
url = "https://www.googleapis.com/customsearch/v1"
total_images = 15 # Total number of images to download
images_per_request = 5  # Maximum number of images per request

client = EmbeddingPredictionClient(project=PROJECT_ID)


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
              all_images.extend(item['link'] for item in data['items'])
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
        [image_link, """Give me a very brief description of the purpose of this image"""],
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
    with ThreadPoolExecutor(max_workers=10) as executor:
      # Soumettre toutes les tâches en une seule étape

        futures = {executor.submit(generate, url): url for url in items_links}
        #print(futures)
        
        # Utilisation de as_completed pour itérer sur les futures au fur et à mesure qu'ils sont terminés
        for future in as_completed(futures):
            url = futures[future]
            try:
                caption = future.result()
            except Exception as e:
                pass
                # Si vous voulez voir la trace complète de l'exception, vous pouvez utiliser traceback
            else:
                captions[url] = caption
    # À ce stade, toutes les tâches sont terminées
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
    captions = image_captioning_parallel(images)
    df_items = pd.DataFrame(list(captions.items()), columns=['ImageURL', 'Caption'])
    if not df_items.empty and len(df_items) > 0:
        return image_selection(query, client, df_items)
    elif df_items.empty:
        print("No items in the DataFrame.")
        return None  # ou une valeur par défaut
    elif len(df_items) == 0:
        print("DataFrame has zero rows.")
        return None  # ou une valeur par défaut
