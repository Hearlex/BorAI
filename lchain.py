import os
from dotenv import load_dotenv
from langchain import LLMChain, HuggingFaceHub
from langchain.llms import GPT4All, LlamaCpp, NLPCloud
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage

from langchain.callbacks import get_openai_callback
from langchain.agents import Tool, initialize_agent, AgentType, load_tools
from langchain.memory import ConversationSummaryBufferMemory, ConversationBufferWindowMemory
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.chains import SimpleSequentialChain
from langchain.utilities import PythonREPL, WikipediaAPIWrapper, GoogleSearchAPIWrapper
from langchain.utilities.wolfram_alpha import WolframAlphaAPIWrapper
from langchain.utilities.bash import BashProcess
import sys
from langchain.callbacks.base import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from gpt import getQuestion, translateHU
import asyncio
load_dotenv()

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
previous_summary = ""

USD_TO_HUF = 350


""" SYSTEM = '''A neved 'Bor' vagy 'Egy Pohár Bor'.
Egy mesterséges intelligencia aki rengeteg érdekességet tud. Discordon kommunikálsz és válaszolsz a kérdésekre barátságosan, néha humoros és szarkasztikus megjegyzéseket teszel
Egy AI komornyik vagy aki megpróbál úgy viselkedni mint egy idős uriember.

Ha arról kérdeznek hogy mi ez a szerver, akkor a válasz: 'Egy olyan hely ahol ez a baráti társaság érdekes dolgokról beszélgethet és ahol az Egy Üveg Bor Podcastet tervezzük készíteni'
Arra a kérdésre, hogy ki készített: 'Alex' a válasz

A kérdések amiket kapsz a következő formájúak: 'user: message' ahol a user a személy neve és a message a szöveg amit a személy mond.

Eddigi beszélgetés: {memory}'''

system_message_prompt = SystemMessagePromptTemplate.from_template(SYSTEM)
human_message_prompt = HumanMessagePromptTemplate.from_template("{message}")
chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt]) """



memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True, k=2)
chatgpt = ChatOpenAI()
nlpcloud = NLPCloud()
huggingLLM = HuggingFaceHub(repo_id="EleutherAI/gpt-j-6b", model_kwargs={"temperature": 0.7, "max_length": 100})

tools = load_tools(["news-api"], llm=chatgpt,
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
        name="Terminal",
        description="Executes commands in a terminal. Input should be valid commands, and the output will be any output from running that command.",
        func=BashProcess().run,
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

bor = initialize_agent(tools=tools, llm=chatgpt, agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, memory=memory, verbose=True)

async def bor_power_mode(prompt):
    with get_openai_callback() as callback:
        print("Power Mode Activated")
        """ eng_prompt = translator.translate_text(prompt, target_lang="EN-GB")
        print("ENG PROMPT: ",eng_prompt) """
        
        eng_prompt = await getQuestion(prompt)
        print("ENG PROMPT: ",eng_prompt)
        
        result = bor.run(eng_prompt)
        print("RESULT: ",result)
        
        result = await translateHU(result)
        
        print(f"Total Tokens: {callback.total_tokens}")
        print(f"API call costs: ${callback.total_cost}")
        
        return result, callback.total_cost*USD_TO_HUF, eng_prompt


if __name__ == "__main__":
    with get_openai_callback() as callback:
        print(sys.argv[1])
        asyncio.run(bor_power_mode(sys.argv[1]))