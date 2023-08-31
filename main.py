import datetime
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
server = None

async def addVoteOptions(message):
    await message.add_reaction('👍')
    await message.add_reaction('👎')

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
    

@bot.command(description='Do something the command asks for')
async def command(ctx, command: discord.Option(str, description='the command to run'), data: discord.Option(str, description='the data to run the command with', required=False)):
    channel = ctx.channel
    await ctx.respond(f'Running command: {command} with data: {data}', ephemeral=True)
    await modules['chat'].commandChat(command, channel, data)
    

# DnD Commands
dndgroup = bot.create_group('dnd', 'DnD Commands')

@dndgroup.command(description='Create a new DnD Character')
@discord.ext.commands.has_role('DnD')
async def createcharacter(ctx,
        character_name: discord.Option(str, description='the name of the character'),
        character_race: discord.Option(str, description='the race of the character'),
        character_class: discord.Option(str, description='the class of the character')
    ):

    low_class = character_class.lower()
    low_race = character_race.lower()
    
    real_class = [cls for cls in modules['dnd'].classes if low_class in cls]
    real_race = [rc for rc in modules['dnd'].races if low_race in rc]

    if len(real_class) != 1:
        await ctx.respond(f'Invalid class: {character_class}', ephemeral=True)
        return
    if len(real_race) != 1:
        await ctx.respond(f'Invalid race: {character_race}', ephemeral=True)
        return


    await ctx.respond(f'Creating character with name: {character_name}, race: {real_race[0]}, class: {real_class[0]}', ephemeral=True)
    await modules['dnd'].create_player(ctx.author , character_name=character_name, character_race=real_race[0], character_class=real_class[0])

@dndgroup.command(description='Join a DnD Mission')
@discord.ext.commands.has_role('DnD')
async def join(ctx):
    thread = ctx.channel
    message = (await thread.history(limit=1,oldest_first=True).flatten())[0]
    try:
        join = await modules['dnd'].join_mission(ctx.author, message)
        if join:
            await ctx.respond('Joined mission', ephemeral=True)
        else:
            await ctx.respond('Sorry! You cannot join this game.', ephemeral=True)
    except Exception as e:
        await ctx.respond(f'Failed to join mission: {e}', ephemeral=True)
        raise e

@dndgroup.command(description='Leave a DnD Mission')
@discord.ext.commands.has_role('DnD')
async def leave(ctx):
    thread = ctx.channel
    message = (await thread.history(limit=1,oldest_first=True).flatten())[0]
    try:
        leave = await modules['dnd'].leave_mission(ctx.author, message)
        if leave:
            await ctx.respond('Left mission', ephemeral=True)
        else:
            await ctx.respond('Failed to leave mission', ephemeral=True)
    except Exception as e:
        await ctx.respond(f'Failed to leave mission: {e}', ephemeral=True)

@dndgroup.command(description='Spectate a DnD Mission')
@discord.ext.commands.has_role('DnD')
async def spectate(ctx):
    thread = ctx.channel
    message = (await thread.history(limit=1,oldest_first=True).flatten())[0]
    try:
        spectate = await modules['dnd'].spectate_mission(ctx.author, message)
        if spectate:
            await ctx.respond('Spectating mission', ephemeral=True)
        else:
            await ctx.respond('Sorry! You cannot spectate this game.', ephemeral=True)
    except Exception as e:
        await ctx.respond(f'Failed to spectate mission: {e}', ephemeral=True)

@dndgroup.command(description='Unspectate a DnD Mission')
@discord.ext.commands.has_role('DnD')
async def unspectate(ctx):
    thread = ctx.channel
    message = (await thread.history(limit=1,oldest_first=True).flatten())[0]
    try:
        unspectate = await modules['dnd'].unspectate_mission(ctx.author, message)
        if unspectate:
            await ctx.respond('Unspectating mission', ephemeral=True)
        else:
            await ctx.respond('Failed to unspectate mission', ephemeral=True)
    except Exception as e:
        await ctx.respond(f'Failed to unspectate mission: {e}', ephemeral=True)

@dndgroup.command(description='Create a new mission')
@discord.ext.commands.has_role('Creator')
async def createmission(ctx,
        name: discord.Option(str, description='the name of the mission'),
        description: discord.Option(str, description='the description of the mission'),
        type: discord.Option(str, description='the type of the mission'),
        difficulty: discord.Option(str, description='the difficulty of the mission'),
        reward: discord.Option(str, description='the reward of the mission'),
        location: discord.Option(str, description='the location of the mission', required=False),
        time: discord.Option(str, description='the time of the mission', required=False),
        player_range: discord.Option(str, description='the range of players for the mission', required=False),
        blacklist: discord.Option(str, description='the list of players who cannot join', required=False),
        whitelist: discord.Option(str, description='the list of players who are able to join', required=False),
    ):
    try:
        if player_range:
            player_range = player_range.split('-')
            player_range = (int(player_range[0]), int(player_range[1]))
            
        if time:
            # Check if time is valid
            time = datetime.datetime.strptime(time, "%Y-%m-%d")
            time = time.strftime("%Y-%m-%d")
            
        await ctx.respond(f'Creating mission with name: {name}, description: {description}, type: {type}, difficulty: {difficulty}, reward: {reward}, location: {location}, time: {time}', ephemeral=True)
        await modules['dnd'].post_mission(name, description, type, difficulty, reward,  location, time, player_range, blacklist, whitelist)
    except Exception as e:
        await ctx.respond(f'Failed to modify mission: {e}', ephemeral=True)
        raise e

@dndgroup.command(description='Modify a mission')
@discord.ext.commands.has_role('Creator')
async def modifymission(ctx,
        name: discord.Option(str, description='the name of the mission'),
        description: discord.Option(str, description='the description of the mission', required=False),
        type: discord.Option(str, description='the type of the mission', required=False),
        difficulty: discord.Option(str, description='the difficulty of the mission', required=False),
        reward: discord.Option(str, description='the reward of the mission', required=False),
        location: discord.Option(str, description='the location of the mission', required=False),
        time: discord.Option(str, description='the time of the mission', required=False),
        player_range: discord.Option(str, description='the range of players for the mission', required=False),
        players: discord.Option(str, description='the list of players', required=False),
        spectators: discord.Option(str, description='the list of spectators', required=False),
        blacklist: discord.Option(str, description='the list of players who cannot join', required=False),
        whitelist: discord.Option(str, description='the list of players who are able to join', required=False),
    ):
    try:
        if player_range:
            player_range = player_range.split('-')
            player_range = (int(player_range[0]), int(player_range[1]))
            
        if time:
            # Check if time is valid
            time = datetime.datetime.strptime(time, "%Y-%m-%d")
            time = time.strftime("%Y-%m-%d")
            
        await ctx.respond(f'Modifying mission with name: {name}, description: {description}, type: {type}, difficulty: {difficulty}, reward: {reward}, location: {location}, time: {time}', ephemeral=True)
        await modules['dnd'].update_mission(name, description, type, difficulty, reward, location, time, player_range, players=players, spectators=spectators, blacklist=blacklist, whitelist=whitelist)
    except Exception as e:
        await ctx.respond(f'Failed to modify mission: {e}', ephemeral=True)

@dndgroup.command(description='End a mission')
@discord.ext.commands.has_role('Creator')
async def endmission(ctx):
    thread = ctx.channel
    message = (await thread.history(limit=1,oldest_first=True).flatten())[0]
    try:
        await modules['dnd'].end_mission(message)
        await ctx.respond('Ended mission', ephemeral=True)
    except Exception as e:
        await ctx.respond(f'Failed to end mission: {e}', ephemeral=True)

bot.run(token)