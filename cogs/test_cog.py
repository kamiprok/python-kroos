from discord.ext import commands
import kroos


class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx):
        reddit = kroos.reddit_start()
        print(reddit.read_only)
        await ctx.send(reddit.read_only)


def setup(bot):
    bot.add_cog(TestCog(bot))
