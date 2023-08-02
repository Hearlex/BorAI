from termcolor import cprint
from lchain import bor_power_mode
from error import MessageError

from langchain.agents import initialize_agent, Tool, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.schema import SystemMessage
from langchain.tools import StructuredTool
from gpt import getQuestion, translateHU, generatePrompt, generateSystemPrompt

import asyncio
import re

from lchain import bor_power_mode

class ChatModule():
    errorMessages = ['Hmm... 🤔', 'Hát figyelj én nem tudom', 'Fogalmam sincs mit akarsz', 'Mivan?', 'Bruh', '💀', 'lol', 'Tesó mi lenne ha nem?', '🤡', 'Bocs én ezt nem', 'Nekem elveim is vannak azért', 'Nézd... ez nem működik', 'Mi lenne ha csak barátokként folytatnánk?', "Sprechen sie deutsch?", 'Megtudnád ismételni?', 'Nem értem', 'Szerintem ezt ne is próbáld meg újra', 'Anyád tudja hogy miket művelsz itt?', 'Játsszuk azt, hogy én ezt most nem hallottam...']
    
    def __init__(self, bot, modules):
        self.bot = bot
        self.modules = modules
        llm = ChatOpenAI(temperature=1, model="gpt-3.5-turbo-0613")
        tools = [
            Tool(
                name="internet-search",
                func=bor_power_mode,
                description="Lehetővé teszi az interneten való keresést. Időjárást vagy egyéb valós idejű információkat is megtud keresni. A bemenet egy keresési kifejezés."
            ),
            Tool(
                name="image-generation",
                func=self.imageGenerationTask,
                description="Generál egy képet a megadott prompt alapján. A bemenet egy prompt és egy opciók JSON objektum ami a következőket tartalmazza: Size:Tupple(2):Int, Anime:Bool. A Size a kép méretét adja meg, az Anime pedig, hogy anime stílusban készüljön-e el a kép."
            )
        ]

        agent_kwargs = {
            "system_message": SystemMessage(content=generateSystemPrompt()),
        }
        self.bor = initialize_agent(llm=llm, tools=tools, agent=AgentType.OPENAI_MULTI_FUNCTIONS, agent_kwargs=agent_kwargs, verbose=True)

        
    def imageGenerationTask(self, message):
        try:
            asyncio.create_task(self.modules['imgprompt'].generateImage(message))
            return "A kép hamarosan elkészül... Tájékoztasd a felhasználód arról, hogy a kép hamarosan elkészül."
        except Exception as e:
            return f"Hiba történt a kép generálása közben: {e}"
        
    async def messageLogic(self, message):
        try:
            answerable_reference = False
            ref_msg = None
            if message.reference is not None:
                print('Reference found')
                ref_msg = await message.channel.fetch_message(message.reference.message_id)
                if ref_msg.author.id == self.bot.user.id:
                    answerable_reference = True

            channel_blacklist = ['Bor Change Log']
            match = re.search('Bor([.,:$!? ]|$)', message.content)
                    
            if (match != None or answerable_reference) and message.channel.name not in channel_blacklist:
                await self.modules['imgprompt'].changeChannel(message.channel)
                
                async with message.channel.typing():
                    with get_openai_callback() as callback:
                        question = message.content
                        
                        if answerable_reference:
                            cprint(f"Reference message: {ref_msg.content}", 'light_yellow')
                        cprint(f"Question: {question}", 'yellow')
                        
                        answer = self.bor.run(f'"{ref_msg.content}"\n\n{question}') if answerable_reference else self.bor.run(question)
                        
                        await self.sendChat(message, answer)
                        
                    print(f"Total Tokens: {callback.total_tokens}")
                    print(f"API call costs: ${callback.total_cost} - {callback.total_cost*340} Ft")
                    
        except Exception as e:
            raise MessageError(e) from e
                            
    async def sendChat(self, message, text):
        print('Sending chat')
        if text.startswith('Bor:'):
            text = text[4:]
        elif text.startswith('Egy Pohár Bor:'):
            text = text[14:]
        elif text.startswith('**Bor:**'):
            text = text[8:]
        await message.channel.send(text)
    
    async def commandChat(self, command, channel, data=None):
        command = f'Most egy programot fogsz futtatni, írd ki a program kimenetét, ahogy Bor válaszolna a parancsra. A parancs: {command} Hozzátartozó adat: {data}. Add vissza a kimenetet a következő üzenetben.'
        answer = self.bor.run(command)
        
        if answer.startswith('Bor:'):
            answer = answer[4:]
        elif answer.startswith('Egy Pohár Bor:'):
            answer = answer[14:]
        elif answer.startswith('**Bor:**'):
            answer = answer[8:]
        
        await channel.send(answer)