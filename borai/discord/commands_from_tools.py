import typing
from typing import Any, Callable, Generic, TypeVar
from typing_extensions import Annotated
import discord
from discord.ext import commands
import borai.tools as tools
import inspect

F = TypeVar('F', bound=Callable[..., Any])

class copy_signature(Generic[F]):
    def __init__(self, target: F) -> None:
        self.target = target
    def __call__(self, wrapped: Callable[..., Any], ctx) -> F:
        return ctx.send(self.target())

def commands_from_tools(bot: discord.Bot):
    """
    Get the list of tools and register them as discord bot commands.
    """
    
    print("Registering test command")
    @bot.command(description='Do something the command asks for')
    @commands.has_role('Creator')
    async def test(ctx, text: discord.Option(str, description='the text to write', required=True)):
        await ctx.send(text)
    
    index = 0
    for tool in tools.tools:
        sign = inspect.signature(tool.run)
        params = [x for x in sign.parameters]
        print(f"Registering command for {tool.name}")
        print(f"type: {type(tool.run)}")
        print(f"Signature: {sign}")
        print(f"Parameters: {params}")
        
        code = f"""
@bot.command(name=tool.name, description=tool.description)
async def command_function(ctx, {str(sign)[1:]}:
    await ctx.send(tools.tools[{index}].run({",".join(params)}))"""
            
        print(code)
        exec(code, globals(), locals())