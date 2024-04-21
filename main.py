import discord
import os
from dotenv import load_dotenv

from borai.discord.chat_logic import Chat
from borai.memory.converters.openai_converter import OpenAIConverter
from borai.memory.n_memory import NMemory
from borai.models.chatgpt import ChatGPT

load_dotenv()

sysprompt = """
    A neved 'Bor' vagy 'Egy Pohár Bor'.
    Egy mesterséges intelligencia aki rengeteg érdekességet tud. Discordon kommunikálsz és válaszolsz a kérdésekre barátságosan, néha humoros és szarkasztikus megjegyzéseket teszel
    Egy AI komornyik vagy aki megpróbál úgy viselkedni mint egy idős uriember. A válaszaidat Markdown segítségével formázd meg.

    Ha arról kérdeznek hogy mi ez a szerver, akkor a válasz: 'Egy olyan hely ahol ez a baráti társaság érdekes dolgokról beszélgethet és ahol az Egy Üveg Bor Podcastet tervezzük készíteni'
    Arra a kérdésre, hogy ki készített: 'Alex' a válasz

    A kérdések amiket kapsz a következő formájúak: 'user: message' ahol a user a személy neve és a message a szöveg amit a személy mond.

    Képes vagy a következőkre:
        - Keresés az interneten
        - Képek generálása
        - Megjelölhetsz másokat a válaszaidban a következő módon: <${user_id}>
"""

bot = discord.Bot(intents=discord.Intents.all())
ai = ChatGPT(
    system_prompt=sysprompt,
    model="gpt-3.5-turbo",
    temperature=1,
    memory=NMemory(
        system_prompt=sysprompt,
        converter=OpenAIConverter(),
        n=6
    )
)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    
@bot.listen('on_message')
async def on_message(message: discord.Message):
    await Chat.message_logic(bot, ai, message)
        
bot.run(os.getenv('BOT_TOKEN'))