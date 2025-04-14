import os
from termcolor import cprint

from dotenv import load_dotenv

def getenv(name: str) -> str:
    # Refresh environment variables
    load_dotenv()
    
    # Get the environment variable value
    variable = os.getenv(name)

    if variable == None:
        cprint(f"Error: '{name}' environment variable is missing.", "red")
        exit(1)

    return variable