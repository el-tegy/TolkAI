import os
from dotenv import load_dotenv
import requests
import threading
import warnings
import time
import numpy as np
from IPython.display import Image, display
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from concurrent.futures import ThreadPoolExecutor
from vertexai.preview.generative_models import GenerativeModel, Part  # Assurez-vous que cette importation est nécessaire et correcte
# call algorithms
from algorithms import jaccard_similarity, image_selection_jaccard, image_selection_levenshtein, image_selection_bert, image_selection_lsa, image_selection_manhattan, image_selection_cosine
# Ingore all TensorFlow warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.simplefilter('ignore')

load_dotenv()

# Enregistrer le temps de début
start_time = time.time()

# Configuration de l'API
API_URL = os.getenv("API_URL")
headers = {"Authorization": f"Bearer{os.getenv('HEADERS')}"}

url = "https://www.googleapis.com/customsearch/v1"
params = {
    "cx": "b3cc7e87732c140e9",
    "key": "AIzaSyANitOObhh9yTC7Sd6GdiLQGcLJgI1Tz7E",
    "searchType": "image",
    "num": 10
}

def query_from_url(image_url):
    """
    Envoie une requête à l'API BLIP Image Captioning pour obtenir la description d'une image.

    :param image_url: URL de l'image à décrire.
    :return: Réponse JSON de l'API ou None en cas d'erreur.
    """
    try:
        data = {"url": image_url}
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()  # Cela va lever une exception pour les réponses HTTP non réussies
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête vers BLIP Image Captioning API: {e}")
        return None

def generate(image_link):
    """
    Génère une description pour une image donnée en utilisant un modèle de génération de contenu.

    :param image_link: URL de l'image.
    :return: Description textuelle de l'image.
    """
    # Implémentez votre logique de génération ici. Actuellement, la fonction est un placeholder.
    # Remplacez par la logique appropriée selon votre modèle de génération de contenu.
    model = GenerativeModel("gemini-pro-vision")
    responses = model.generate_content(
        [image_link, """Give short description of this image"""],
        generation_config={
            "max_output_tokens": 200,
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

def image_search(query):
    """
    Recherche d'images sur Google Custom Search avec une requête spécifique.

    :param query: Requête de recherche.
    :return: Liste des items (images) retournés par la recherche.
    """
    params['q'] = query
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get('items', [])
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête Google Custom Search: {e}")
        return []

# Fonction de recherche d'images Bing
def search_images_bing(query):
    """
    Effectue une recherche d'images sur Bing avec une requête spécifique.

    :param user_query: Requête de recherche.
    :return: Liste des items (images) retournés par la recherche.
    """
    subscription_key = os.getenv('BING_SEARCH_V7_SUBSCRIPTION_KEY')
    endpoint = f"{os.getenv('BING_SEARCH_V7_ENDPOINT')}/v7.0/images/search"

    params = {'q': query, 'mkt': 'en-US', 'count': 25}
    headers = {'Ocp-Apim-Subscription-Key': subscription_key}

    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("value", [])
    except Exception as ex:
        print(f"Erreur lors de la requête Bing Image Search: {ex}")
        return []
    
def process_individual_image(link, combined_texts):
    """
    Traite une image individuelle pour obtenir sa description et l'ajoute à une liste.

    :param link: URL de l'image.
    :param combined_texts: Liste des descriptions collectées.
    """
    description = generate(link)
    if description:
        combined_texts.append(description)

def image_captioning(list_of_items):
    """
    Génère des descriptions pour une liste d'images en utilisant du multithreading.

    :param list_of_items: Liste des items (images) à traiter.
    :return: Liste des descriptions textuelles des images.
    """
    combined_texts = []
    items_links = [item['contentUrl'] for item in list_of_items]
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_individual_image, link, combined_texts) for link in items_links]
        for future in futures:
            future.result()  # Attendre que chaque tâche soit terminée

    return combined_texts

# def image_selection(list_of_combined_texts, items, query):
#     """
#     Sélectionne l'image la plus pertinente en fonction des descriptions et de la requête initiale.

#     :param list_of_combined_texts: Liste des descriptions des images.
#     :param items: Liste des items (images) correspondants.
#     :param query: Requête de recherche initiale.
#     :return: URL de l'image la plus pertinente.
#     """
#     combined_texts = [query] + list_of_combined_texts
#     vectorizer = TfidfVectorizer()
#     tfidf_matrix = vectorizer.fit_transform(combined_texts)
#     cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
#     most_similar_idx = cosine_similarities.argsort()[0][-1]
#     return items[most_similar_idx]['contentUrl']

def image_selection(list_of_combined_texts, items, query, algorithm='lsa'):    
    if algorithm == 'jaccard':
        return image_selection_jaccard(list_of_combined_texts, items, query)
    elif algorithm == 'levenshtein':
        selected_image = image_selection_levenshtein(list_of_combined_texts, items, query)
    elif algorithm == 'bert':
        selected_image = image_selection_bert(list_of_combined_texts, items, query)
    elif algorithm == 'cosine':
        selected_image = image_selection_cosine(list_of_combined_texts, items, query)
    elif algorithm == 'lsa':
        selected_image = image_selection_lsa(list_of_combined_texts, items, query)
    elif algorithm == 'manhattan':
        selected_image = image_selection_manhattan(list_of_combined_texts, items, query)
    # autres conditions pour différents algorithmes...
    return selected_image

def image_retrieval_pipeline(image_label):
    """
    Pipeline complet pour la récupération de l'image la plus pertinente basée sur une requête.

    :param image_label: Étiquette ou description de l'image recherchée.
    :return: URL de l'image la plus pertinente.
    """
    items = search_images_bing(image_label)
    if not items:
        return "Aucune image trouvée pour la requête spécifiée."

    combined_texts = image_captioning(items)
    if not combined_texts:
        return "Aucune description n'a pu être générée pour les images trouvées."

    image_link = image_selection(combined_texts, items, image_label)
    return image_link

# Exemple d'utilisation
print(image_retrieval_pipeline("Power BI Desktop window with the 'Get Data' button highlighted"))

# Enregistrer le temps de fin
end_time = time.time()

# Calculer et afficher la durée d'exécution
duration = end_time - start_time
print(f"Temps d'exécution total : {duration} secondes soit {round(duration/60, 2)} minutes")