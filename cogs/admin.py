import discord
from discord.ext import commands
import kroos
import requests


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def imgur(self, ctx):
        response = requests.get('https://imgur.com/random')
        item = response.url
        await ctx.send(item)


def setup(bot):
    print('cogs.admin module loaded')
    bot.add_cog(Admin(bot))


def teardown(bot):
    print('cogs.admin module unloaded')
