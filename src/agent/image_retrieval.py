import streamlit as st
import requests
import vertexai
import concurrent.futures
from vertexai.preview.generative_models import GenerativeModel
from google.oauth2 import service_account
import requests
import concurrent.futures
from vertexai.preview.generative_models import GenerativeModel
import difflib

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["service_account"])

PROJECT_ID = 'ping38'
params = {
    "cx": "b3cc7e87732c140e9",
    "key": "AIzaSyANitOObhh9yTC7Sd6GdiLQGcLJgI1Tz7E",
    "searchType": "image",
    "fileType": "BMP, GIF, JPEG, PNG"
}

vertexai.init(
    project='ping38',
    credentials=credentials
)


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


dictionnaire = {
    "Image of the 'get data' button in Power BI": "https://learn.microsoft.com/en-us/power-bi/connect-data/media/desktop-connect-to-data/get-data-from-web.png",
    "Image of the'save' button in Power BI": "https://monashdatafluency.github.io/Power_BI/figures/ch04/save.png",
    "Image of the'publish' button in Power BI": "https://learn.microsoft.com/en-us/power-bi/collaborate-share/media/service-publish-to-web/power-bi-more-options-publish-web.png",
    "Image of the duplicate column button in Power Query": "https://www.myexcelonline.com/wp-content/uploads/2017/10/Duplicate-Columns-03.png",
    "Image of the'filter' button in Power Query": "https://excelunlocked.com/wp-content/uploads/2020/10/Text-Filters-in-Power-Query-Editor.png",
    "Image of the'Pie chart' in Power BI": "https://cdn.educba.com/academy/wp-content/uploads/2020/02/Power-BI-Pie.png",
    "Image of the'Insert' tab in Word":"https://learn.microsoft.com/en-us/previous-versions/aspnet/images/dd465337.ocp_publish_web_settings_tab_with_cf_and_non_cf_databases(vs.110).png",
    "Image of the'Pictures' button in the 'Insert' tab":"https://www.wikihow.com/images/thumb/a/ac/Set-Tabs-in-a-Word-Document-Step-2-Version-2.jpg/v4-460px-Set-Tabs-in-a-Word-Document-Step-2-Version-2.jpg.webp",
    "Image of the'Insert Picture' dialog box":"https://www.automateexcel.com/excel/wp-content/uploads/2021/10/insert-function-dialog-box-4.png",
    "Image of the'Save' button in the 'File' tab":"https://www.learningcomputer.com/images/word_insert_tab.jpg",
    "Image of the'Publish' button in the 'File' tab":"https://teststeststests.com/wp-content/uploads/2021/08/4-GS-the-file-tab.gif",
    "Image of the fields pane in Power BI":"https://k21academy.com/wp-content/uploads/2021/07/Screenshot-61.png",
    "Image of the slicer in Power BI":"https://cdn.educba.com/academy/wp-content/uploads/2020/03/Slicers-In-Power-BI.png",
    "Image of the'merge tables' button in Power Query":"https://community.powerbi.com/t5/image/serverpage/image-id/238402iC4CB2E6CF5B2DC65/image-size/large?v=1.0&px=999",
    "Image of the undo button in Power Query in Power BI":"https://cdn-5a6cb102f911c811e474f1cd.closte.com/wp-content/uploads/2018/02/Main-Areas-of-the-Power-Query-Editor.png",
    "Image of the 'New Measure' button in Power BI":"https://learn.microsoft.com/en-us/power-bi/transform-model/media/desktop-tutorial-create-measures/meastut_netsales_newmeasure.png",
    "Image of the'Measure' field in Power BI":"https://learn.microsoft.com/en-us/power-bi/transform-model/media/desktop-measures/measuresinpbid_measinfieldlist.png",
    "Image of the'change type' option in Power Query":"https://learn.microsoft.com/en-us/power-query/media/data-types/right-click.png",
    "Image of the slicer in the visualizations pane in Power BI":"https://www.enjoysharepoint.com/wp-content/uploads/2021/07/Power-BI-Slicer-4-1536x623.png",
    "Image of the 'Data Type' drop-down list in Power Query":"https://learn.microsoft.com/en-us/power-bi/connect-data/media/desktop-data-types/pbiddatatypesinqueryeditort.png",
    "Image of the 'Data' view in Power BI":"https://miro.medium.com/max/3840/1*ysFfkvTMXiD5dyZcKuBg-Q.png",
    "Image of the 'Formula Bar' in Power BI":"https://i0.wp.com/blog.enterprisedna.co/wp-content/uploads/2020/08/1-21.png",
    "Image of the 'Merge Queries' button in Power BI":"https://www.acuitytraining.co.uk/wp-content/uploads/2021/12/Power-BI-Merge-Queries-and-Append-Queries-4-650x247.png",
    "Image of the 'Join kind' options in Power BI":"https://pbitraining.bizdata.com.au/dataprep/lab_1_transforming_data/use_power_query_editor/merging/MergeWizard2.jpg",
    "Image of the 'Query Editor' in Power BI":"https://absentdata.com/wp-content/uploads/2019/07/query-editor.png",
    "Image of the 'Merge Editor' window in Power BI":"https://www.acuitytraining.co.uk/wp-content/uploads/2021/12/Power-BI-Merge-Queries-and-Append-Queries-4-650x247.png"
}

def trouver_correspondance(query, dictionnaire):
    # Liste des clés du dictionnaire
    cles = list(dictionnaire.keys())

    # Utilisation de la bibliothèque difflib pour trouver la correspondance la plus proche
    correspondance = difflib.get_close_matches(query, cles, n=1, cutoff=0.9)

    # Vérifier si une correspondance a été trouvée
    if correspondance:
        # Renvoyer la valeur correspondante dans le dictionnaire
        return dictionnaire[correspondance[0]]
    else:
        return None


def image_retrieval_pipeline(query_list):
    url = "https://www.googleapis.com/customsearch/v1"
    total_images = 30  # Total number of images to download
    images_per_request = 5  # Maximum number of images per request
    query_list = query_list.split(";")
    list_relevant_image=[]
    for query in query_list:
        most_relevant_image = trouver_correspondance(query, dictionnaire)
        if most_relevant_image is not None:
            print("most rel " +query)
            list_relevant_image.append(most_relevant_image)
        else:
            print("search "+query)
            query = query.replace("button", "")
            image_urls = image_search(query=query, total_images=total_images, images_per_request=images_per_request,
                                    url=url)
            formatted_prompt = format_for_generate(image_urls, query)
            response = generate(formatted_prompt)
            most_relevant_image = response[2:-2].replace(" ", "")
            list_relevant_image.append(most_relevant_image)
    return list_relevant_image

# Assuming list_url is a global set
def multiple_query_image_retrieval(query):
    # Use a set comprehension to directly generate the set
    list_url = {image_retrieval_pipeline(element) for element in query.split(";")}
    print(list_url)
    return list_url

def multiple_query_image_retrieval2(query):
    # Split the query string
    queries = query.split(",")

    # Use concurrent.futures.ThreadPoolExecutor for parallelization
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Use submit to submit each task and get futures
        futures = {executor.submit(image_retrieval_pipeline, q): q for q in queries}

        # Use as_completed to get results in order of completion
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
        print(results)
    return results