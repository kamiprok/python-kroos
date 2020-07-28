import discord
from discord.ext import commands
import kroos
from asyncio import sleep


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role('Admin' or 'Mod')
    async def warn(self, ctx, user: discord.Member, seconds: int):
        role = discord.utils.get(user.guild.roles, name='Warned')
        await user.add_roles(role)
        await ctx.send(f'{user.display_name} warned for {seconds} seconds')
        await sleep(seconds)
        await user.remove_roles(role)
        await ctx.send(f"{user.display_name}'s warn is over")

    @warn.error  # caches errors for warn command
    async def warn_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('/warn {user} {seconds}')

    @commands.command()
    @commands.has_role('Admin' or 'Mod')
    async def bonk(self, ctx, user: discord.Member, seconds: int):
        user_roles = []
        for role in user.roles:
            user_roles.append(role)
        muted = [discord.utils.get(user.guild.roles, name='Muted')]
        await user.edit(roles=muted)
        await ctx.send(f'{user.display_name} bonked for {seconds} seconds')
        await sleep(seconds)
        await user.edit(roles=user_roles)
        await ctx.send(f"{user.display_name}'s timeout is over")

    @commands.command()
    @commands.has_role('Admin' or 'Mod')
    async def unbonk(self, ctx, user: discord.Member):
        role = [discord.utils.get(user.guild.roles, name='Member')]
        await user.edit(roles=role)
        await ctx.send(f'{user.display_name} force unbonked. Temp role Member added until bonk time runs out')

    @bonk.error  # caches errors for bonk command
    async def bonk_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('/bonk {user} {seconds}')

    @commands.command()
    @commands.has_role('Admin')
    @commands.has_permissions(administrator=True)
    async def task(self, ctx, task: str):  # use "" to parse 2 words as one string
        if task in ('change status', '1'):
            await ctx.message.author.send(f'{kroos.change_status.get_task()}')
        elif task in ('random message', '2'):
            await ctx.message.author.send(f'{kroos.random_message.get_task()}')
        else:
            await ctx.message.author.send(f'{kroos.change_status.get_task()}\n'
                                          f'{kroos.random_message.get_task()}')

    @commands.command()
    @commands.has_role('Admin')
    @commands.has_permissions(administrator=True)
    async def stop(self, ctx, task: str):
        if task in ('change status', '1'):
            kroos.change_status.cancel()
            await ctx.send(f'Change status background task stopped')
        elif task in ('random message', '2'):
            kroos.random_message.cancel()
            await ctx.send(f'Random message background task stopped')
        else:
            kroos.change_status.cancel()
            kroos.random_message.cancel()
            await ctx.send(f'All background tasks stopped')

    @commands.command()
    @commands.has_role('Admin')
    @commands.has_permissions(administrator=True)
    async def start(self, ctx, task: str):
        if task in ('change status', '1'):
            kroos.change_status.start()
            await ctx.send(f'Change status background task started')
        elif task in ('random message', '2'):
            kroos.random_message.start()
            await ctx.send(f'Random message background task started')
        else:
            kroos.change_status.start()
            kroos.random_message.start()
            await ctx.send(f'All background tasks started')

    @commands.command()
    @commands.has_role('Admin')
    @commands.has_permissions(administrator=True)
    async def restart(self, ctx, task: str):
        if task in ('change status', '1'):
            kroos.change_status.restart()
            await ctx.send(f'Change status background task restarted')
        elif task in ('random message', '2'):
            kroos.random_message.restart()
            await ctx.send(f'Random message background task restarted')
        else:
            kroos.change_status.restart()
            kroos.random_message.restart()
            await ctx.send(f'All background tasks restarted')

    @commands.command()
    @commands.has_role('Admin')
    @commands.has_permissions(administrator=True)
    async def shutdown(self, ctx):
        await ctx.send(f'Shutting down')
        await ctx.bot.logout()


def setup(bot):
    print('cogs.admin module loaded')
    bot.add_cog(Admin(bot))


def teardown(bot):
    print('cogs.admin module unloaded')
