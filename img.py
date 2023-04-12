from imggen import generateImage


class ImgModule():
    def __init__(self, bot):
        self.bot = bot
        
    async def createImage(self, prompt, options):
        try:
            if 'size' in options.keys() and 'anime' in options.keys():
                return await generateImage(prompt, size=(options['size']), anime=True)
            elif 'size' in options.keys():
                return await generateImage(prompt, size=(options['size']))
            elif 'anime' in options.keys():
                return await generateImage(prompt, anime=True)
            else:
                return await generateImage(prompt)
        except Exception as e:
            raise e