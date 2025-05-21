import requests
from typing_extensions import Annotated
from borai.tools.tool_base import ToolBase
from termcolor import cprint

class DictionaryTool(ToolBase):
    """A tool to look up definitions of words."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_url = "https://api.dictionaryapi.dev/api/v2/entries/en/"

    def run(self, word: Annotated[str, "The word to find the definition for."]) -> Annotated[str, "The definition of the word, or an error message if not found."]:
        """Looks up the definition of a word using a public API.

        Args:
            word (str): The word to define.

        Returns:
            str: A formatted string containing the definitions, or an error message.
        """
        try:
            response = requests.get(f"{self.api_url}{word}")
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            
            data = response.json()
            cprint(f"Dictionary API response for '{word}': {data}", "light_grey")

            if isinstance(data, dict) and data.get("title") == "No Definitions Found":
                return f"Sorry, I couldn't find a definition for '{word}'."

            definitions = []
            for entry in data:
                for meaning in entry.get("meanings", []):
                    part_of_speech = meaning.get("partOfSpeech", "N/A")
                    for definition_obj in meaning.get("definitions", []):
                        def_text = definition_obj.get("definition")
                        if def_text:
                            definitions.append(f"({part_of_speech}) {def_text}")
            
            if not definitions:
                return f"Sorry, I found an entry for '{word}' but it contained no clear definitions."

            return f"Definitions for '{word}':\n" + "\n".join(definitions)

        except requests.exceptions.HTTPError as http_err:
            cprint(f"HTTP error occurred: {http_err} - Response: {response.text}", "red")
            return f"Sorry, an error occurred while fetching the definition for '{word}'. The dictionary service might be unavailable."
        except requests.exceptions.RequestException as req_err:
            cprint(f"Request error occurred: {req_err}", "red")
            return f"Sorry, a network error occurred while trying to reach the dictionary service for '{word}'."
        except Exception as e:
            cprint(f"An unexpected error occurred in DictionaryTool: {e}", "red")
            return f"An unexpected error occurred while looking up '{word}'."

if __name__ == '__main__':
    # For testing the tool directly
    tool = DictionaryTool()
    test_word = "example"
    print(f"Looking up '{test_word}':")
    print(tool.run(test_word))
    print("\nLooking up 'nonexistentwordxyz':")
    print(tool.run('nonexistentwordxyz'))
    print("\nLooking up 'lead':") # A word with multiple meanings
    print(tool.run('lead'))
