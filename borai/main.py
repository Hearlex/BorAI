import discord
import os
from dotenv import load_dotenv

from discord.chat_logic import Chat
from models.chatgpt import ChatGPT

load_dotenv()

bot = discord.Bot(intents=discord.Intents.all())
ai = ChatGPT(
    system_prompt="""
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
    """,
    model="gpt-3.5-turbo",
    temperature=1
)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    
@bot.listen('on_message')
async def on_message(message: discord.Message):
    try:
        if message.author == bot.user:
            return
        
        answerable_reference = False
        if message.reference is not None:
                ref_msg = await message.channel.fetch_message(message.reference.message_id)
                if ref_msg.author.id == bot.user.id:
                    answerable_reference = True
                    
        if str(bot.user.id) in message.content or answerable_reference:
            response = ai.run(message.content)
            await Chat.send_chat(channel=message.channel, message=response)
        
    except Exception as e:
        print(e)
        await Chat.send_chat(channel=message.channel, message=Chat.error_message())
        
bot.run(os.getenv('BOT_TOKEN'))