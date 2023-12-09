import re
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from vertexai.language_models import ChatModel

chat_model = ChatModel.from_pretrained("chat-bison")
parameters = {
    "max_output_tokens": 1024,
    "temperature": 0.2,
    "top_p": 0.8,
    "top_k": 40
}

chat = chat_model.start_chat(
    context="""""",
)
response = chat.send_message("""\"Provide me with a step by step guide to create a heat map chart in Power BI Desktop (include images in each step of the guide so that I can easily follow up)\"""", **parameters)

# Votre texte contenant les chaînes entre crochets
your_text = response.text

relevant_link="\n"
# Images Description provide by the LLM
images_description = re.findall(r'\[(.*?)\]', your_text)

API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
headers = {"Authorization": "Bearer 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"}

#Description of the images retrieve by the LLLM of hugging face
def query_from_url(image_url):
    data = {"url": image_url}
    response = requests.post(API_URL, headers=headers, json=data)
    return response.json()

#Retrieve the most relevent images in google search
def image_search(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "cx": "b3cc7e87732c140e9",
        "key": "AIzaSyANitOObhh9yTC7Sd6GdiLQGcLJgI1Tz7E",
        "searchType": "image",
        "num":2
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data

for text in images_description:

    text+="in Power BI desktop"
    #Retrieve the images which fit the description
    result=image_search(text)
    items = result['items']
    #Get the links of these images
    images_links=[item['link'] for item in items]

    combined_texts=[]
    #Get the description of this images
    for image_link in images_links:
        try:
            output = query_from_url(image_link)
            resume=output[0]['generated_text']
            combined_texts.append(resume)

            combined_texts.insert(0, text)
        except Exception as e:
            pass
    # Create a TF-IDF Vectorizer object
    vectorizer = TfidfVectorizer()

    # Tokenize and build vocab
    tfidf_matrix = vectorizer.fit_transform(combined_texts)

    # Calculate cosine similarity between the user query and all items
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])

    # Get the index of the most similar item
    most_similar_idx = cosine_similarities.argsort()[0][-1]

    # Select the most relevant item
    most_relevant_item = items[most_similar_idx]

    relevant_link+=most_relevant_item['link']
    relevant_link+='\n'



print(f"{response.text}\n {relevant_link}")