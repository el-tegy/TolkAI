import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from vertexai.preview.generative_models import GenerativeModel, Part
#from IPython.display import Image, display


API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
headers = {"Authorization": "Bearer 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"}

url = "https://www.googleapis.com/customsearch/v1"


params = {
    "cx": "b3cc7e87732c140e9",
    "key": "AIzaSyANitOObhh9yTC7Sd6GdiLQGcLJgI1Tz7E",
    "searchType": "image",
    "num":10
}


def query_from_url(image_url):
    data = {"url": image_url}
    response = requests.post(API_URL, headers=headers, json=data)
    return response.json()

def generate(image_link):
    model = GenerativeModel("gemini-pro-vision")
    responses = model.generate_content(
        [image_link, """Describe this image"""],
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

def image_search(query):
    params['q']=query
    response = requests.get(url, params=params)
    data = response.json()
    items=data['items']
    return items

def image_captioning(list_of_items):
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
    combined_texts=list_of_combined_texts
    combined_texts.insert(0, query)
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(combined_texts)
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
    most_similar_idx = cosine_similarities.argsort()[0][-1]
    most_relevant_item = items[most_similar_idx]
    return most_relevant_item['link']

def image_retrieval_pipeline(image_label):
    items = image_search(image_label)
    combined_texts = image_captioning(items)
    image_link = image_selection(combined_texts, items, image_label)
    return image_link

#print(image_retrieval_pipeline("Power BI Desktop window with the 'Get Data' button highlighted"))