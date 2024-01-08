import requests
import concurrent.futures
from vertexai.preview.generative_models import GenerativeModel

PROJECT_ID = 'ping38'
params = {
    "cx": "b3cc7e87732c140e9",
    "key": "AIzaSyANitOObhh9yTC7Sd6GdiLQGcLJgI1Tz7E",
    "searchType": "image",
    "fileType": "BMP, GIF, JPEG, PNG"
}

def fetch_data(url, params):
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if 'items' in data:
            return [item['link'] for item in data['items']]
        else:
            return []
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def image_search(query, total_images, images_per_request, url):
    all_images = []
    params["q"] = query
    params["num"] = images_per_request
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for start_index in range(1, total_images + 1, images_per_request):
            params_copy = params.copy()
            params_copy["start"] = start_index
            futures.append(executor.submit(fetch_data, url, params))

        for future in concurrent.futures.as_completed(futures):
            all_images.extend(future.result())

    return all_images

def format_for_generate(image_urls, query):
    formatted_list = ['"""Here is a python list of link of images :[']
    
    for url in image_urls:
        formatted_list.append(f'\'""", """{url}""", """\'')
        formatted_list.append(", '")

    # Remove the last comma and quote
    if formatted_list:
        formatted_list.pop()

    # Add closing brackets
    formatted_list.append(']')
    pre = '\"'
    footer = f"""Now, here is a criterion for the relevance of images: {pre[0]}{query}{pre[0]}"
    Have a carefull look at each image in the list provided before and select the image that illustrates the most \ 
    the previous criterion among that list of images. Then, return a python list containing only the link of that best image among all."""
    formatted_list.append(footer)
    
    formatted_list.append('"""]')


    return formatted_list

def generate(formatted_prompt):
    model = GenerativeModel("gemini-pro-vision")
    responses = model.generate_content(
        formatted_prompt,
        generation_config={
            "max_output_tokens": 2048,
            "temperature": 0.2,
            "top_p": 1,
            "top_k": 32
        },
    stream=True,
    )
    return " ".join([response.candidates[0].content.parts[0].text for response in responses])

def image_retrieval_pipeline(query):
    url = "https://www.googleapis.com/customsearch/v1"
    total_images = 40 # Total number of images to download
    images_per_request = 5  # Maximum number of images per request
    query = query.replace("button", "")
    image_urls = image_search(query=query, total_images=total_images, images_per_request=images_per_request, url=url)
    formatted_prompt = format_for_generate(image_urls, query)
    response = generate(formatted_prompt)
    most_relevant_image = response[2:-2].replace(" ", "")
    return most_relevant_image