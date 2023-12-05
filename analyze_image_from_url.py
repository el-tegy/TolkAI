import os
from google.cloud import vision_v1
from google.cloud.vision_v1 import types
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./ping38-593be1a1e8c6.json"

# Initialize the Cloud Vision API client
client = vision_v1.ImageAnnotatorClient()
#Algorithm to tcheck the label and score of the image
def analyze_image_from_url(image_url):
    client = vision_v1.ImageAnnotatorClient()

    # Specify the image URL
    image = vision_v1.Image()
    image.source.image_uri = image_url

    # Specify the features you want to extract
    features = [types.Feature(type_=types.Feature.Type.LABEL_DETECTION)]

    # Make the API request
    request = types.AnnotateImageRequest(image=image, features=features)
    response = client.annotate_image(request)

    # Process the response
    labels = response.label_annotations
    for label in labels:
        print(f"Label: {label.description}, Score: {label.score}")