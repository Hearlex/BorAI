from modules.image.imggen import generateImage
import os
import discord

class ImgModule():
    def __init__(self, bot):
        self.bot = bot
        
    async def createImage(self, prompt, options, message):
        try:
            keys = options.keys()
            img_size = options['size'] if 'size' in keys else (512, 512)
            img_anime = 'anime' in keys

            imgPaths =  await generateImage(prompt, size=img_size, anime=img_anime)
            for path in imgPaths:
                if os.path.exists(path):
                    await message.channel.send(file=discord.File(path))
                    os.remove(path)
        except Exception as e:
            raise e