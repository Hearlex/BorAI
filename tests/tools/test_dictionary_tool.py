import unittest
from unittest.mock import patch, MagicMock
import requests

# Add borai to sys.path if tests are run from the root directory or tests directory
# This ensures that 'from borai.tools.dictionary_tool import DictionaryTool' works
import sys
import os
# Get the absolute path of the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from borai.tools.dictionary_tool import DictionaryTool

class TestDictionaryTool(unittest.TestCase):

    def setUp(self):
        self.tool = DictionaryTool()

    @patch('requests.get')
    def test_run_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "word": "example",
                "phonetics": [
                    {"text": "/ɪɡˈzɑːmpəl/", "audio": "https://api.dictionaryapi.dev/media/pronunciations/en/example-uk.mp3"}
                ],
                "meanings": [
                    {
                        "partOfSpeech": "noun",
                        "definitions": [
                            {
                                "definition": "A thing characteristic of its kind or illustrating a general rule.",
                                "example": "it's a good example of how European action can produce results"
                            }
                        ]
                    },
                    {
                        "partOfSpeech": "verb",
                        "definitions": [
                            {
                                "definition": "Be or represent a typical sample or instance of (something).",
                                "example": "the extent to which the romances are exampled in manuscript"
                            }
                        ]
                    }
                ]
            }
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        expected_output = "Definitions for 'example':\n(noun) A thing characteristic of its kind or illustrating a general rule.\n(verb) Be or represent a typical sample or instance of (something)."
        self.assertEqual(self.tool.run("example"), expected_output)
        mock_get.assert_called_once_with("https://api.dictionaryapi.dev/api/v2/entries/en/example")

    @patch('requests.get')
    def test_run_word_not_found(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "title": "No Definitions Found",
            "message": "Sorry pal, we couldn't find definitions for the word you were looking for.",
            "resolution": "You can try the search again at later time or head to the web instead."
        }
        mock_response.raise_for_status = MagicMock() # Simulate no HTTP error for "not found"
        mock_get.return_value = mock_response

        expected_output = "Sorry, I couldn't find a definition for 'nonexistentword'."
        self.assertEqual(self.tool.run("nonexistentword"), expected_output)
        mock_get.assert_called_once_with("https://api.dictionaryapi.dev/api/v2/entries/en/nonexistentword")

    @patch('requests.get')
    def test_run_http_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("API is down")
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        expected_output = "Sorry, an error occurred while fetching the definition for 'testword'. The dictionary service might be unavailable."
        self.assertEqual(self.tool.run("testword"), expected_output)

    @patch('requests.get')
    def test_run_request_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        expected_output = "Sorry, a network error occurred while trying to reach the dictionary service for 'testword'."
        self.assertEqual(self.tool.run("testword"), expected_output)
        
    @patch('requests.get')
    def test_run_empty_definitions(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "word": "weirdcase",
                "meanings": [
                    {
                        "partOfSpeech": "noun",
                        "definitions": [] # Empty definitions list
                    }
                ]
            }
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        expected_output = "Sorry, I found an entry for 'weirdcase' but it contained no clear definitions."
        self.assertEqual(self.tool.run("weirdcase"), expected_output)

    @patch('requests.get')
    def test_run_malformed_response_no_meanings(self, mock_get):
        mock_response = MagicMock()
        # Simulate a valid JSON response but without 'meanings' or 'definitions' keys as expected
        mock_response.json.return_value = [ 
            {
                "word": "mysteryword"
                # "meanings" key is missing
            }
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # This should ideally return a "no clear definitions" message or a generic error.
        # Based on current DictionaryTool.run(), it will likely be "no clear definitions".
        expected_output = "Sorry, I found an entry for 'mysteryword' but it contained no clear definitions."
        self.assertEqual(self.tool.run("mysteryword"), expected_output)


if __name__ == '__main__':
    unittest.main()
