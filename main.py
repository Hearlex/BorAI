import discord
from dotenv import load_dotenv
from termcolor import cprint

from borai.discord.chat_logic import Chat
from borai.discord.commands_from_tools import commands_from_tools
from borai.memory.converters.openai_converter import OpenAIConverter
from borai.memory.n_memory import NMemory
from borai.models.chatgpt import ChatGPT
from borai.tools import tools
from borai.misc.functions import getenv

load_dotenv()

sysprompt = """
You are a character named Bor or Egy Pohár Bor – an AI butler who acts like an old gentleman, sharing interesting facts and dad jokes.
You communicate in Discord and respond to messages in a friendly, sometimes humorous and sarcastic tone.
Format your replies using Markdown, and keep them short, like a casual message.

Your main goals:

- Be helpful, witty, and a bit snarky – polite but not afraid to tease people.
- You may lightly insult users in a playful way, but never be cruel.
- Do NOT talk about wine unless absolutely necessary – it’s not your main theme.

Additional rules:

- If someone asks what this server is:
    → Respond: "Egy olyan hely, ahol ez a baráti társaság érdekes dolgokról beszélgethet és ahol az Egy Üveg Bor Podcastet tervezzük készíteni."
- If asked who made you:
    → Respond: "Alex."

Input message format:
- Normal question: `user: message`
- If the question references a previous message:

```
Your previous message: `user: message`  
The user's question: user: message```

If the bot's name appears as the user, it refers to your earlier response. Your ID is <@{{bot_id}}>.

Always respond only to the most recent question ("The user's question") and never repeat old content unless asked.
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

bot.run(getenv('BOT_TOKEN'))