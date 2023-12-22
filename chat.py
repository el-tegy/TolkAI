import requests
import os
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from IPython.display import Image, display
from vertexai.language_models import ChatModel
import warnings

# Ingore all TensorFlow warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.simplefilter('ignore')

load_dotenv()

def get_power_bi_response(user_query, temperature=0.2):
    # Chat model for generating text
    chat_model = ChatModel.from_pretrained("chat-bison")

    # Parameters for chat model
    parameters = {
        "temperature": temperature,
        "max_output_tokens": 1024,
        "top_p": 0.95,
        "top_k": 40,
    }

    # Start the chat with a context related to Power BI
    chat = chat_model.start_chat(
        context="You are an exper in Power BI analytic tool. \n Add images to your response. Use the Power BI documentation to add the right image"
    )

    response_text = chat.send_message(user_query, **parameters).text

    items_links = search_images_on_google(user_query)

    combine_text_and_image(response_text, items_links)

    # return combined_response

def search_images_on_google(user_query):
    
    # For specific search on Poer BI documentation
    # site_specific_query = f"{user_query} site:microsoft.com"
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": user_query,
        "cx": "b3cc7e87732c140e9",
        "key":os.getenv("API_KEY"),
        "searchType": "image",
        "num":10
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if 'items' in data:
        items_links = [item['link'] for item in data['items']]
        return items_links
    else:
        print("Aucun résultat trouvé.")
        return []

def query_from_url(image_url):
    api_url_ = os.getenv("API_URL")
    headers_ = {"Authorization": os.getenv("HEADERS")}
    
    data = {"url": image_url}
    response = requests.post(api_url_, headers=headers_, json=data)
    return response.json()

def combine_text_and_image(response_text, items_links):
    combined_texts = []

    for item in items_links:
        output = query_from_url(item)
        resume = output[0]['generated_text']
        combined_texts.append(resume)

    # Create a TF-IDF Vectorizer object
    vectorizer = TfidfVectorizer()

    # Tokenize and build vocab
    tfidf_matrix = vectorizer.fit_transform(combined_texts)

    # Calculate cosine similarity between the user query and all items
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])

    # Get the index of the most similar item
    most_similar_idx = cosine_similarities.argsort()[0][-1]

    # Select the most relevant item
    most_relevant_item = items_links[most_similar_idx]


    print("Response from Palm2 model\n\n", response_text)
    print(most_relevant_item)

    # Fetch the image and display it
    # response = requests.get(most_relevant_item)

    # # Check if the request was successful (status code 200)
    # if response.status_code == 200:
    #     # Display the image in the notebook
    #     print("\n\n")
    #     display(Image(data=response.content))
    # else:
    #     print("Error downloading the image. Status code:", response.status_code)


if __name__ == "__main__":
    user_query = "How to create a histogram in Power BI step by step"
    get_power_bi_response(user_query)
