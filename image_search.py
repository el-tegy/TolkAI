import requests

url = "https://www.googleapis.com/customsearch/v1"
params = {
    "q": "Image of the Power BI Desktop application with the 'Get Data' button highlighted",
    "cx": <>,
    "key": <>,
    "searchType": "image"
}
response = requests.get(url, params=params)
data = response.json()

# Process and use the data as needed
print(data['items'])