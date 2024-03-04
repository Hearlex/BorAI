from agentlogic import bor, user_proxy
from tools import get_weather_info, google_search

question = input(">>> ")
user_proxy.initiate_chat(bor, message=question)