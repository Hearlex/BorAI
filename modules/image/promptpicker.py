import discord
from discord.ext import pages, commands
from discord.ui.input_text import InputText
import asyncio

from gpt import generateImagePrompt

class PromptView(discord.ui.View):
        def __init__(self, prompt, message, imggen, timeout=180):
            super().__init__(timeout=timeout)
            self.prompt = prompt
            self.message = message
            self.imggen = imggen
            self.options = {}
        
        @discord.ui.button(label='Elfogadom', style=discord.ButtonStyle.success, emoji='✅')
        async def accept(self, button: discord.ui.Button, interaction: discord.Interaction):
            try:
                await interaction.response.edit_message(view=None)
                await self.imggen.createImage(self.prompt, self.options, self.message)
            except Exception as e:
                print(e)
            
        @discord.ui.button(label='Módosítom', style=discord.ButtonStyle.primary)
        async def modify(self, button: discord.ui.Button, interaction: discord.Interaction):
            try:
                await interaction.response.send_modal(EditPromptModal(prompt=self.prompt, message=self.message, imggen=self.imggen))
            except Exception as e:
                print(e)
        
        @discord.ui.button(label='Elutasítom', style=discord.ButtonStyle.danger, emoji='🚫')
        async def decline(self, button: discord.ui.Button, interaction: discord.Interaction):
            try:
                await interaction.response.edit_message(content='Elutasítottad', view=None, delete_after=5)
                await self.message.delete()
            except Exception as e:
                print(e)

class EditPromptModal(discord.ui.Modal):
    def __init__(self, prompt, message, imggen):
        super().__init__(title='Prompt módosítása')
        self.options = {}
        self.message = message
        self.imggen = imggen
        
        self.add_item(InputText(label='Új prompt', required=True, value=prompt, style=discord.InputTextStyle.long))
    
    async def callback(self, interaction: discord.Interaction):
        try:
            prompt = self.children[0].value
            await interaction.response.edit_message(content=f'Módosítottad a promptot: {prompt}', view=None)
            await self.imggen.createImage(prompt, self.options, self.message)
        except Exception as e:
            print(e)
            
class ImageGenerator():
    def __init__(self, bot, imggen):
        self.bot = bot
        self.imggen = imggen
        self.channel = None
        self.options = {}
        
    async def changeChannel(self, channel):
        self.channel = channel
    
    async def generateImage(self, message):
        prompt = await generateImagePrompt(message)
        await self.channel.send(f'Az következő promptot generáltam: {prompt}', view=PromptView(prompt, message, self.imggen))