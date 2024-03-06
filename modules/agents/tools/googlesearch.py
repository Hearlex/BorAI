import requests
from dotenv import load_dotenv
import os
from typing_extensions import Annotated

load_dotenv()

def get_important_info(results):
    important_info = []
    for result in results:
        title = result["title"]
        link = result["link"]
        snippet = result["snippet"]
        important_info.append((title, link, snippet))
    return important_info

def google_search(query: Annotated[str, "The query to search with on google."], max_results: Annotated[int, "The maximum number of results to return."] = 10) -> Annotated[list, "A list of tuples containing the title, link and snippet of the search results."]:
    api_key = os.getenv("GOOGLE_API_KEY")
    cx_id = os.getenv("GOOGLE_CSE_ID")
    url = "https://www.googleapis.com/customsearch/v1"

    params = {
        "key": api_key,
        "cx": cx_id,
        "q": query,
        "num": max_results
    }

    response = requests.get(url, params=params)
    results = response.json()["items"]
    return get_important_info(results)

if __name__ == "__main__":
    print(google_search("python", max_results=5))