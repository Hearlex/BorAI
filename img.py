from imggen import generateImage


class ImgModule():
    def __init__(self, bot):
        self.bot = bot
        
    async def createImage(self, prompt, options):
        try:
            keys = options.keys()
            img_size = options['size'] if 'size' in keys else (512, 512)
            img_anime = 'anime' in keys

            return await generateImage(prompt, size=img_size, anime=img_anime)
        except Exception as e:
            raise e