from discord.ext import commands


class ToolBase():
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.name = self.__class__.__name__.lower()
        self.description = self.__doc__
        
        for key, value in kwargs.items():
            setattr(self, key, value)

    def run(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)