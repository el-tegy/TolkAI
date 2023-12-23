import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from IPython.display import Image, display


API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
headers = {"Authorization": "Bearer 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"}

url = "https://www.googleapis.com/customsearch/v1"

user_query = "Image of the 'Get Data' button in the Home tab"
user_query+="in Power BI desktop"

params = {
    "q": user_query,
    "cx": "b3cc7e87732c140e9",
    "key": "AIzaSyANitOObhh9yTC7Sd6GdiLQGcLJgI1Tz7E",
    "searchType": "image",
    "num":50
}


def query_from_url(image_url):
    data = {"url": image_url}
    response = requests.post(API_URL, headers=headers, json=data)
    return response.json()


def image_search_and_caption(query):
    combined_texts=[]
    #params['q']=query
    response = requests.get(url, params=params)
    data = response.json()
    print(data)
    items = data['items']
    items_links=[item['link'] for item in items]
    for item in items_links:
        output = query_from_url(item)
        resume=output[0]['generated_text']
        combined_texts.append(resume)
    return combined_texts

def image_selection(a_list):
    combined_texts=a_list
    combined_texts.insert(0, user_query)
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(combined_texts)
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
    most_similar_idx = cosine_similarities.argsort()[0][-1]
    most_relevant_item = items[most_similar_idx]
    return most_relevant_item['link']

def image_retrieval_pipeline(query):
    combined_texts = image_search_and_caption(query)
    image_link = image_selection(combined_texts)
    return image_link
    

user_query = "Image of the 'Get Data' button in the Home tab"
user_query+="in Power BI desktop"

print(image_retrieval_pipeline(user_query))