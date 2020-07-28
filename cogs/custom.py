import discord
from discord.ext import commands
import kroos
from asyncio import sleep


class Custom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role('Admin')
    @commands.has_permissions(administrator=True)
    async def test(self, ctx):
        await ctx.send('done <:donkey:733436132347347005>')

    @commands.command()
    @commands.has_role('Admin' or 'Mod')
    async def warn2(self, ctx, user: discord.Member, seconds: int):
        warned = discord.utils.get(user.guild.roles, name='Warned')
        await user.add_roles(warned)
        await ctx.send(f'{user.display_name} warned for {seconds} seconds')
        await sleep(seconds)
        await user.remove_roles(warned)
        await ctx.send(f"{user.display_name}'s warn is over")

    @commands.command()
    @commands.has_role('Admin')
    @commands.has_permissions(administrator=True)
    async def custom(self, ctx):
        embed = discord.Embed(title='Kroos')
        name = kroos.db.kroos.find_one({'_id': 4})["name"]
        value = kroos.db.kroos.find_one({'_id': 4})["value"]
        embed.add_field(name=name, value=value)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_role('Admin')
    @commands.has_permissions(administrator=True)
    async def update(self, ctx, name: str, value: str):
        custom = {'_id': 4}
        edited = {f'$set': {'name': name, 'value': value}}
        kroos.db.kroos.update_one(custom, edited)
        await ctx.send('Custom command updated')


def setup(bot):
    print('cogs.custom module loaded')
    bot.add_cog(Custom(bot))


def teardown(bot):
    print('cogs.custom module unloaded')
