import discord
import os
from dotenv import load_dotenv
from chat import ChatModule
import asyncio
import random
from modules.image.img import ImgModule
import json
from modules.image.promptpicker import ImageGenerator
from modules.dnd.dnd import DnD

load_dotenv()
token = os.getenv('BOT_TOKEN')
bot = discord.Bot(intents=discord.Intents.all())

modules = {}

async def addVoteOptions(message):
    await message.add_reaction('👍')
    await message.add_reaction('👎')

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    modules['img'] = ImgModule(bot)
    modules['imgprompt'] = ImageGenerator(bot, modules['img'])
    modules['chat'] = ChatModule(bot, modules)
    modules['dnd'] = DnD(bot)

@bot.listen('on_message')
async def on_message(message):
    try:
        if message.author == bot.user:
            return

        if message.channel.id == 1138382043156316180:
            emoteTask = asyncio.create_task(addVoteOptions(message))
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
    
@bot.command(description='Remind DnD Users to vote!')
async def reminddnd(ctx):
    channel = ctx.channel
    await ctx.respond("Processing...", ephemeral=True)
    answer = await modules['dnd'].show_likes()
    print(answer)
    answer = str(answer)
    
    await modules['chat'].commandChat('Küldj egy üzenetet az összes dnd felhasználónak akik 0, 1 vagy 2 szavazatot adtak le a kampánytémákra! Jelezd nekik, hogy hétvégéig van még idejük szavazni. A leadott szavazatokat egy JSON-ben kapod meg, amik {"felhasználónév": szavazatok száma} formátumban van megadva.', channel, answer)

@bot.command(description='Do something the command asks for')
async def command(ctx, command: discord.Option(str, description='the command to run'), data: discord.Option(str, description='the data to run the command with', required=False)):
    channel = ctx.channel
    await ctx.respond(f'Running command: {command} with data: {data}', ephemeral=True)
    await modules['chat'].commandChat(command, channel, data)

bot.run(token)