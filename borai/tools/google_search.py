import requests
from termcolor import cprint
from typing_extensions import Annotated
from discord.ext import commands

from borai.tools.tool_base import ToolBase
from borai.misc.functions import getenv

class GoogleSearchTool(ToolBase):
    """A tool for performing Google searches and retrieving important information from the search results."""

    def __init__(self, *args, **kwargs):
        self.api_key = getenv("GOOGLE_API_KEY")
        self.cx_id = getenv("GOOGLE_CSE_ID")
        self.url = "https://www.googleapis.com/customsearch/v1"
        super().__init__(*args, **kwargs)
    
    def get_important_info(self, results):
        """Extracts important information from the search results.

        Args:
            results (list): The search results.

        Returns:
            list: A list of tuples containing the title, link, and snippet of the search results.

        """
        important_info = []
        for result in results:
            title = result["title"]
            link = result["link"]
            snippet = result["snippet"]
            important_info.append((title, link, snippet))
        return important_info

    def google_search(self, query: Annotated[str, "The query to search with on google."], max_results: Annotated[int, "The maximum number of results to return."] = 10) -> Annotated[list, "A list of tuples containing the title, link and snippet of the search results."]:
        """Performs a Google search and returns a list of tuples containing the title, link, and snippet of the search results.

        Args:
            query (str): The query to search with on Google.
            max_results (int, optional): The maximum number of results to return. Defaults to 10.

        Returns:
            list: A list of tuples containing the title, link, and snippet of the search results.

        """
        api_key = getenv("GOOGLE_API_KEY")
        cx_id = getenv("GOOGLE_CSE_ID")
        url = "https://www.googleapis.com/customsearch/v1"

        params = {
            "key": api_key,
            "cx": cx_id,
            "q": query,
            "num": max_results
        }

        response = requests.get(url, params=params)
        cprint(response.json(), "light_grey")
        results = response.json()["items"]
        return self.get_important_info(results)
    
    def run(self, query: Annotated[str, "The query to search with on google."], max_results: Annotated[int, "The maximum number of results to return."] = 10):
        """Runs a Google search with the given query and maximum number of results.

        Args:
            query (str): The query to search with on Google.
            max_results (int, optional): The maximum number of results to return. Defaults to 10.

        Returns:
            list: A list of tuples containing the title, link, and snippet of the search results.

        """
        return self.google_search(query, max_results)
