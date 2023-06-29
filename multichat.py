from langchain.agents import initialize_agent, Tool, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
import sys
import asyncio
from gpt import getQuestion, translateHU

from lchain import bor_power_mode

llm = ChatOpenAI(temperature=1, model="gpt-3.5-turbo-0613")
tools = [
    Tool(
        name="power_bor",
        func=bor_power_mode,
        description="Search the web for the answer to your question. Input should be a search query."
    )
]

bor = initialize_agent(llm=llm, tools=tools, agent=AgentType.OPENAI_MULTI_FUNCTIONS, verbose=True)

if __name__ == "__main__":
    with get_openai_callback() as callback:
        print(sys.argv[1])
        try:
            question = getQuestion(sys.argv[1])
        except:
            question = sys.argv[1]
        
        
        answer = bor.run(question)
        
        try:
            print(translateHU(answer))
        except:
            print(answer)
        
    print(f"Total Tokens: {callback.total_tokens}")
    print(f"API call costs: ${callback.total_cost} - {callback.total_cost*340} Ft")