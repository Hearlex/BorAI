
import random

import discord


errorMessages = [
    'Hmm... 🤔',
    'Hát figyelj én nem tudom',
    'Fogalmam sincs mit akarsz',
    'Mivan?',
    'Bruh',
    '💀',
    'lol',
    'Tesó mi lenne ha nem?',
    '🤡',
    'Bocs én ezt nem',
    'Nekem elveim is vannak azért',
    'Nézd... ez nem működik',
    'Mi lenne ha csak barátokként folytatnánk?',
    "Sprechen sie deutsch?",
    'Megtudnád ismételni?',
    'Nem értem',
    'Szerintem ezt ne is próbáld meg újra',
    'Anyád tudja hogy miket művelsz itt?',
    'Játsszuk azt, hogy én ezt most nem hallottam...'
]

class Chat():
    
    @classmethod
    def error_message(cls) -> str:
        return random.choice(errorMessages)
    
    @classmethod
    async def send_chat(cls, channel: discord.TextChannel, message: str):
        await channel.send(message)