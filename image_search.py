import requests

url = "https://www.googleapis.com/customsearch/v1"
params = {
<<<<<<< HEAD
    "q": "An image showing how to get data with power bi desktop",
    "cx": "d5a58fd2521514055",
    "key": "AIzaSyANitOObhh9yTC7Sd6GdiLQGcLJgI1Tz7E",
=======
    "q": "Image of the Power BI Desktop application with the 'Get Data' button highlighted",
    "cx": <>,
    "key": <>,
>>>>>>> bcec05904a14f58989b4e4ef9a3fcdd29edc9ace
    "searchType": "image"
}
response = requests.get(url, params=params)
data = response.json()

items = data['items']
items_links=[item['link'] for item in items]
print(items_links)
for link in items_links:
    items_and_links={}
    items_and_links[link]=link.split('https://learn.microsoft.com/en-us/power-bi/')[1].split('/')
    print(items_and_links)
    