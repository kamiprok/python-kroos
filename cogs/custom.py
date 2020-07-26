import discord
from discord.ext import commands
import kroos


class Custom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role('Admin')
    @commands.has_permissions(administrator=True)
    async def test(self, ctx):
        reddit = kroos.reddit_start()
        print(reddit.read_only)
        await ctx.send(reddit.read_only)
        for x in kroos.db.kroos.find({'_id': 1}):
            print(x)
        await ctx.send('done')

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
