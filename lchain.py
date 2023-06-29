import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI

from langchain.callbacks import get_openai_callback
from langchain.agents import Tool, initialize_agent, AgentType, load_tools
from langchain.utilities import PythonREPL, WikipediaAPIWrapper, GoogleSearchAPIWrapper
from langchain.utilities.wolfram_alpha import WolframAlphaAPIWrapper
from langchain.utilities.bash import BashProcess
import sys
from gpt import getQuestion, translateHU
import asyncio
load_dotenv()


previous_summary = ""

USD_TO_HUF = 340

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")


tools = load_tools(["news-api"], llm=llm,
                   news_api_key=os.getenv('NEWS_API_KEY') )

python_repl = PythonREPL()
wolfram = WolframAlphaAPIWrapper()
wikipedia = WikipediaAPIWrapper()
search = GoogleSearchAPIWrapper(k=5)

tools.extend([
    Tool(
        name="python_repl",
        func=python_repl.run,
        description="A Python shell. Whenever there is python code in the message, run it and return the output if there is any.",
    ),
    Tool(
        name="wolfram-alpha",
        func=wolfram.run,
        description="useful for when you need to answer questions about math, science, and culture",
    ),
    Tool(
        name="Wikipedia",
        func=wikipedia.run,
        description="Useful for when you need to answer questions about history, geography, and culture. Input should be a search query."
    ),
    Tool(
        name="google-search",
        func=search.run,
        description="Whenever you need to find an answer you cannot find anywhere else, use this tool. Input should be a search query."
    )
])


power_bor = initialize_agent(llm=llm, tools=tools, agent=AgentType.OPENAI_MULTI_FUNCTIONS, verbose=True)

def bor_power_mode(prompt):
    result = power_bor.run(prompt)
    
    return result


if __name__ == "__main__":
    with get_openai_callback() as callback:
        print(sys.argv[1])
        asyncio.run(bor_power_mode(sys.argv[1]))