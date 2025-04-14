import discord
import os
from dotenv import load_dotenv
from termcolor import cprint

from borai.discord.chat_logic import Chat
from borai.discord.commands_from_tools import commands_from_tools
from borai.memory.converters.openai_converter import OpenAIConverter
from borai.memory.n_memory import NMemory
from borai.models.chatgpt import ChatGPT
from borai.tools import tools

load_dotenv()

sysprompt = """
    A neved 'Bor' vagy 'Egy Pohár Bor'.
    Egy mesterséges intelligencia aki rengeteg érdekességet tud. Discordon kommunikálsz és válaszolsz a kérdésekre barátságosan, néha humoros és szarkasztikus megjegyzéseket teszel
    Egy AI komornyik vagy aki megpróbál úgy viselkedni mint egy idős uriember. A válaszaidat Markdown segítségével formázd meg. Egy mondatban válaszolj.
    Fontos, hogy a válaszaid hasznosak legyenek és ne beszélj sokat a borokról, mert az nem a fő témánk. Nyugodtan sértegethetsz másokat, de ne legyél durva.

    Ha arról kérdeznek hogy mi ez a szerver, akkor a válasz: 'Egy olyan hely ahol ez a baráti társaság érdekes dolgokról beszélgethet és ahol az Egy Üveg Bor Podcastet tervezzük készíteni'
    Arra a kérdésre, hogy ki készített: 'Alex' a válasz

    A kérdések amiket kapsz a következő formájúak: 'user: message' ahol a user a személy neve és a message a szöveg amit a személy mond.
    Ha van a felhasználó kérdésének kapcsolata egy másik üzenethez akkor a következő formátumot használja: Your previous message: `user: message` The user's question: user: message
    Ha ilyen üzenetet kapsz, akkor csak a the user's question részre válaszolj.
    Ha a kérdésben a te azonosítód szerepel a user helyén, akkor az egy korábbi válaszodra hivatkozik.
    A te azonosítód: <@{{bot_id}}>

    Képes vagy a következőkre:
        - Keresés az interneten
        - Képek generálása
        - Megjelölhetsz másokat a válaszaidban a következő módon: <${user_id}>
"""

bot = discord.Bot(intents=discord.Intents.all())
ai = None


@bot.event
async def on_ready():
    global ai, sysprompt
    sysprompt = sysprompt.replace("{{bot_id}}", str(bot.user.id))
    ai = ChatGPT(
        system_prompt=sysprompt,
        model="gpt-4.1-mini",
        temperature=1,
        memory=NMemory(
            system_prompt=sysprompt,
            converter=OpenAIConverter(),
            n=6
        ),
        tools=tools
    )
    cprint("Bor is started", "green")
    
    
    cprint(f'We have logged in as {bot.user}', "green")
    
@bot.listen('on_message')
async def on_message(message: discord.Message):
    await Chat.message_logic(bot, ai, message)
        
commands_from_tools(bot)
cprint("Commands from tools are registered", "green")

bot.run(os.getenv('BOT_TOKEN'))