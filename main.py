import datetime
import discord
import os
from dotenv import load_dotenv
import asyncio
import random
import json

from chat import ChatModule
from modules.image.img import ImgModule
from modules.image.promptpicker import ImageGenerator
from modules.dnd.dnd import DnD
import commands
global bot, modules

load_dotenv()
token = os.getenv('BOT_TOKEN')
bot = discord.Bot(intents=discord.Intents.all())

modules = {}
server = None

@bot.event
async def on_ready():
    global modules, server
      
    modules['img'] = ImgModule(bot)
    modules['imgprompt'] = ImageGenerator(bot, modules['img'])
    modules['dnd'] = DnD(bot)
    modules['chat'] = ChatModule(bot, modules)
    server = await bot.fetch_guild(1084891853758935141)
    print(f'We have logged in as {bot.user}')

@bot.listen('on_message')
async def on_message(message):
    try:
        if message.author == bot.user:
            return

        #if message.channel.id == 1138382043156316180:
            #emoteTask = asyncio.create_task(addVoteOptions(Smessage))
        messageTask = asyncio.create_task(modules['chat'].messageLogic(message))
        
        await asyncio.gather(messageTask)
    except Exception as e:
        print(e)
        await modules['chat'].sendChat(message, random.choice(modules['chat'].errorMessages))



bot.run(token)