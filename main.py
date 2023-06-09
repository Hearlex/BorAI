import discord
import os
from dotenv import load_dotenv
from chat import ChatModule
import asyncio
import random
from img import ImgModule
import json
from promptpicker import ImageGenerator

load_dotenv()
token = os.getenv('BOT_TOKEN')
bot = discord.Bot(intents=discord.Intents.all())

modules = {}

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    modules['img'] = ImgModule(bot)
    modules['imgprompt'] = ImageGenerator(bot, modules['img'])
    modules['chat'] = ChatModule(bot, modules)

@bot.listen('on_message')
async def on_message(message):
    try:
        if message.author == bot.user:
            return

        #emoteTask = asyncio.create_task(self.emoteLogic(message))
        messageTask = asyncio.create_task(modules['chat'].messageLogic(message))
        
        await asyncio.gather(messageTask)
    except Exception as e:
        print(e)
        await modules['chat'].sendChat(message, random.choice(modules['chat'].errorMessages))

@bot.command(description='generate an image')
async def createimage(ctx, prompt: discord.Option(str, description='the prompt for the image'), options: discord.Option(str, description='the options for the image', required=False)):
    if not options: options = '{}'
    jsonoptions = json.loads(options)
    await ctx.respond(f'Generating Image with prompt: {prompt} and options: {jsonoptions}')
    imgPaths = await modules['img'].createImage(prompt, jsonoptions, ctx.message)
    

bot.run(token)