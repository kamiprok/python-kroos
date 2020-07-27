import discord
from discord.ext import commands
import requests
import kroos


class Custom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role('Admin')
    @commands.has_permissions(administrator=True)
    async def test(self, ctx):
        data = kroos.db.kroos.find_one({'_id': 5})
        today_is: str
        random_wiki: str = 'random_wiki'
        random_sub: str = 'random_sub'
        random_quote: str = 'random_quote'
        random_imgur: str = 'random_imgur'
        for item in data['messages']:
            if item == 'today_is':
                print('Today is var1')
            elif item == random_wiki:
                response = requests.get('https://en.wikipedia.org/wiki/Special:Random')
                item = response.url
                print(item)
            elif item == random_sub:
                for submission in kroos.reddit.subreddit('random').top('day', limit=1):
                    item = submission.shortlink
                    print(item)
            elif item == random_quote:
                response = requests.get('http://quotes.stormconsultancy.co.uk/random.json')
                to_dict = kroos.json.loads(response.text)
                print(f'"{to_dict["quote"]}" - {to_dict["author"]}')
            elif item == random_imgur:
                response = requests.get('https://imgur.com/random')
                item = response.url
                print(item)
            else:
                print(item)

        await ctx.send('done <:donkey:733436132347347005>')

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
