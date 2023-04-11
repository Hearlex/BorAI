from imggen import generateImage


class ImgModule():
    def __init__(self, bot):
        self.bot = bot
        
    async def createImage(self, prompt, options):
        try:
            paths = None
            if 'size' in options.keys() and 'anime' in options.keys():
                paths = await generateImage(prompt, size=(options['size']), anime=True)
            elif 'size' in options.keys():
                paths = await generateImage(prompt, size=(options['size']))
            elif 'anime' in options.keys():
                paths = await generateImage(prompt, anime=True)
            else:
                paths = await generateImage(prompt)
            return paths
        except Exception as e:
            raise e