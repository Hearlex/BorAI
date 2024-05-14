import random
import re
import discord
from termcolor import cprint

from borai.models.ai_interface import AIInterface


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
        
    @classmethod
    async def message_logic(cls, bot, ai: AIInterface, message: discord.Message):
        try:
            if message.author == bot.user:
                return

            answerable_reference = False
            if message.reference is not None:
                try:
                    ref_msg = await message.channel.fetch_message(message.reference.message_id)
                    print(ref_msg.attachments)
                    answerable_reference = True
                except discord.errors.NotFound:
                    print("Message not found")
                    
            images = []
            if len(message.attachments) > 0:
                for attachment in message.attachments:
                    if "image" in attachment.content_type:
                        images.append(attachment.url)
                        
            if answerable_reference and len(ref_msg.attachments) > 0:
                for attachment in ref_msg.attachments:
                    if "image" in attachment.content_type:
                        images.append(attachment.url)

            channel_blacklist = ['Bor Change Log', 'mesterséges-intelligencia', 'videójátékok']
                    
            if (str(bot.user.id) in message.content or answerable_reference) and message.channel.name not in channel_blacklist:
                async with message.channel.typing():
                        question = message.content
                        
                        if answerable_reference:
                            cprint(f"Reference message: {ref_msg.content}", 'light_yellow')
                        cprint(f"Question: {question}", 'yellow')

                        prompt = f"<@{message.author.id}>: {message.content}" if not answerable_reference else f"Your previous message: `<@{ref_msg.author.id}>: {ref_msg.content}`\n\nThe user's question: <@{message.author.id}>: {message.content}"

                        if len(images) > 0:
                            response = ai.run_with_image(prompt, images)
                        else:
                            response = ai.run(prompt)
                        cprint(f"Response: {response}\n", 'green')
                        await cls.send_chat(channel=message.channel, message=response)

        except Exception as e:
            print(e)
            await cls.send_chat(channel=message.channel, message=cls.error_message())
            raise e