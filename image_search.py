import requests

url = "https://www.googleapis.com/customsearch/v1"
params = {
    "q": "Image of the Power BI Desktop application with the 'Get Data' button highlighted",
    "cx": "a46073abb1acd4346",
    "key": "AIzaSyANitOObhh9yTC7Sd6GdiLQGcLJgI1Tz7E",
    "searchType": "image"
}
response = requests.get(url, params=params)
data = response.json()

# Process and use the data as needed
print(data['items'])