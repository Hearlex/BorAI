import requests
from dotenv import load_dotenv
import os
from agentlogic import user_proxy, bor
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

@user_proxy.register_for_execution()
@bor.register_for_llm(name="google_search", description="Search Google for a query.")
def google_search(query, max_results=10):
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
