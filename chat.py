import discord
import asyncio
import json
import random
from termcolor import cprint
from lchain import bor_power_mode

from langchain.agents import initialize_agent, Tool, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.schema import SystemMessage
import sys
import asyncio
from gpt import getQuestion, translateHU, generatePrompt, generateSystemPrompt

from lchain import bor_power_mode

llm = ChatOpenAI(temperature=1, model="gpt-3.5-turbo-0613")
tools = [
    Tool(
        name="internet-search",
        func=bor_power_mode,
        description="Lehetővé teszi az interneten való keresést. Időjárást vagy egyéb valós idejű információkat is megtud keresni. A bemenet egy keresési kifejezés."
    )
]

agent_kwargs = {
    "system_message": SystemMessage(content=generateSystemPrompt()),
}
bor = initialize_agent(llm=llm, tools=tools, agent=AgentType.OPENAI_MULTI_FUNCTIONS, agent_kwargs=agent_kwargs, verbose=True)

class ChatModule():
    errorMessages = ['Hmm... 🤔', 'Hát figyelj én nem tudom', 'Fogalmam sincs mit akarsz', 'Mivan?', 'Bruh', '💀', 'lol', 'Tesó mi lenne ha nem?', '🤡', 'Bocs én ezt nem', 'Nekem elveim is vannak azért', 'Nézd... ez nem működik', 'Mi lenne ha csak barátokként folytatnánk?', "Sprechen sie deutsch?", 'Megtudnád ismételni?', 'Nem értem', 'Szerintem ezt ne is próbáld meg újra', 'Anyád tudja hogy miket művelsz itt?']
    
    def __init__(self, bot):
        self.bot = bot
        
    async def messageLogic(self, message):
        try:
            answerable_reference = False
            ref_msg = None
            if message.reference is not None:
                print('Reference found')
                ref_msg = await message.channel.fetch_message(message.reference.message_id)
                if ref_msg.author.id == self.bot.user.id:
                    answerable_reference = True
                    
            if ('Bor' in message.content or answerable_reference) and message.channel.name != 'Bor Change Log':
                async with message.channel.typing():
                    with get_openai_callback() as callback:
                        question = message.content
                        
                        if answerable_reference:
                            cprint(f"Reference message: {ref_msg.content}", 'light_yellow')
                        cprint(f"Question: {question}", 'yellow')
                        
                        answer = bor.run(question) if not answerable_reference else bor.run(f'"{ref_msg.content}"\n\n{question}')
                        
                        await self.sendChat(message, answer)
                        
                    print(f"Total Tokens: {callback.total_tokens}")
                    print(f"API call costs: ${callback.total_cost} - {callback.total_cost*340} Ft")
                    
        except Exception as e:
            raise Exception(e)
                            
    async def sendChat(self, message, text):
        print('Sending chat')
        if text.startswith('Bor:'):
            text = text[4:]
        elif text.startswith('Egy Pohár Bor:'):
            text = text[14:]
        await message.channel.send(text)
            