import discord
from discord.ext import commands
import kroos
import requests
from asyncio import sleep


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def imgur(self, ctx):
        response = requests.get('https://imgur.com/random')
        item = response.url
        await ctx.send(item)

    @commands.command()
    @commands.has_role('Admin' or 'Mod')
    async def warn(self, ctx, user: discord.Member, seconds: int):
        role = [discord.utils.get(user.guild.roles, name='Warned')]
        await user.add_roles(role)
        await ctx.send(f'{user.display_name} warned for {seconds} seconds')
        await sleep(seconds)
        await user.remove_roles(role)
        await ctx.send(f"{user.display_name}'s warn is over")

    @warn.error  # caches errors for warn command
    async def warn_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('/warn {user} {seconds}')


def setup(bot):
    print('cogs.admin module loaded')
    bot.add_cog(Admin(bot))


def teardown(bot):
    print('cogs.admin module unloaded')
