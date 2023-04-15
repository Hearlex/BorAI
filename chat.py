import discord
import asyncio
import json
import random
from gpt import generateMessage, generateMessageWithReference
from lchain import bor_power_mode

class ChatModule():
    errorMessages = ['Hmm... 🤔', 'Hát figyelj én nem tudom', 'Fogalmam sincs mit akarsz', 'Mivan?', 'Bruh', '💀', 'lol', 'Tesó mi lenne ha nem?', '🤡', 'Bocs én ezt nem', 'Nekem elveim is vannak azért', 'Nézd... ez nem működik', 'Mi lenne ha csak barátokként folytatnánk?', "Sprechen sie deutsch?", 'Megtudnád ismételni?', 'Nem értem', 'Szerintem ezt ne is próbáld meg újra', 'Anyád tudja hogy miket művelsz itt?']
    
    def __init__(self, bot):
        self.bot = bot
        
    async def messageLogic(self, message):
        print('Entered Message Logic')
        try:
            answerable_reference = False
            if message.reference is not None:
                print('Reference found')
                ref_msg = await message.channel.fetch_message(message.reference.message_id)
                if ref_msg.author.id == self.bot.user.id:
                    answerable_reference = True
                    
            if ('Bor' in message.content or answerable_reference) and message.channel.name != 'Bor Change Log':
                intents, options = self.intentDetection(message)
                
                print(f"Intents: {intents}")
                
                async with message.channel.typing():
                    if 'imagegen' in intents:
                        pass
                    elif 'search' in intents and 'search' in [r.name.lower() for r in message.author.roles]:
                        answer, cost, eng_prompt = await bor_power_mode(message.content)
                        await self.sendChat(message, f"*Átfogalmazott keresési kifejezés: {eng_prompt}*")
                        await self.sendChat(message, answer)
                        await self.sendChat(message, f"*A keresési eredmények költsége: {cost} Ft*")
                    else:
                        text, memoryTask = None, None
                        if message.reference is not None:
                            text, memoryTask = await generateMessageWithReference(message.author.name, message.content, message.reference.resolved.author.name, message.reference.resolved.content)
                        else:
                            text, memoryTask = await generateMessage(message.author.name, message.content)
                        text = text.choices[0].message.content
                        await asyncio.gather(self.sendChat(message, text), memoryTask)
        except Exception as e:
            raise Exception(e)
                            
    async def sendChat(self, message, text):
        print('Sending chat')
        if text.startswith('Bor:'):
            text = text[4:]
        elif text.startswith('Egy Pohár Bor:'):
            text = text[14:]
        await message.channel.send(text)
    
    def intentDetection(self, message):
        print('Started Intent Detection')
        intents = []
        options = {}
        try:
            if message.content.startswith('['):
                options = json.loads('{'+message.content[1:(message.content.rfind(']'))]+'}')
                
            if any(gword in message.content.lower() for gword in ['draw', 'generate', 'generálj', 'generálnál', 'generáld', 'rajzolj', 'rajzold', 'képet']): intents.append('imagegen')
            if any(gword in message.content.lower() for gword in ['remind', 'emlékeztess', 'emlékeztetőt', 'szólni', 'szólj']): intents.append('reminder')
            if any(gword in message.content.lower() for gword in ['search', 'keress', 'keresni', 'keresés', 'keresést', 'keresnéd', 'nézz', 'futtasd', 'futtass']): intents.append('search')
        except Exception as e:
            print(e)
            print('{'+message.content[1:(message.content.index(']'))]+'}')
            raise Exception(e)
        return intents, options
            