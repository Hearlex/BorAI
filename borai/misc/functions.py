import os
from termcolor import cprint

def getenv(name: str) -> str:
    variable = os.getenv(name)

    if variable == None:
        cprint(f"Error: '{name}' environment variable is missing.", "red")
        exit(1)

    return variable