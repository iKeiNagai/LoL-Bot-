from twitchio.ext import commands

class HelloComponent(commands.Component):
    def __init__(self, bot):
            self.bot = bot

    @commands.command(name="hello")
    async def hello(self, ctx: commands.Context):
        await ctx.send(f"Hello, {ctx.author.name}!")