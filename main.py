import discord
import os
from dotenv import load_dotenv
from chat import ChatModule
import asyncio
import random
from img import ImgModule
import json

load_dotenv()
token = os.getenv('BOT_TOKEN')
bot = discord.Bot(intents=discord.Intents.all())
chat = ChatModule(bot)
img = ImgModule(bot)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.listen('on_message')
async def on_message(message):
    try:
        if message.author == bot.user:
            return

        #emoteTask = asyncio.create_task(self.emoteLogic(message))
        messageTask = asyncio.create_task(chat.messageLogic(message))
        
        await asyncio.gather(messageTask)
    except Exception as e:
        print(e)
        await chat.sendChat(message, random.choice(chat.errorMessages))

@bot.command(description='generate an image')
async def createimage(ctx, prompt: discord.Option(str, description='the prompt for the image'), options: discord.Option(str, description='the options for the image', required=False)):
    if not options: options = '{}'
    jsonoptions = json.loads(options)
    ctx.respond(f'Generating Image with prompt: {prompt} and options: {jsonoptions}')
    imgPaths = await img.createImage(prompt, jsonoptions)
    for path in imgPaths:
        if os.path.exists(path):
            await ctx.channel.send(file=discord.File(path))
            os.remove(path)
    

bot.run(token)