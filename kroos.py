import discord
from datetime import datetime
from discord.ext import commands
from discord.ext.tasks import loop
import os
import pytz
from random import randrange

TOKEN = os.environ['token']

bot = commands.Bot(command_prefix='/')


async def clock():
    tz = pytz.timezone('Europe/Warsaw')
    clock.now = datetime.now().astimezone(tz)
    clock.day = datetime.today().astimezone(tz).strftime('%a')
    clock.today = clock.now.strftime('%d-%b-%Y')
    clock.time = clock.now.strftime('%H:%M')
    clock.longdate = clock.now.strftime('%A, %d of %B, %Y')
    return clock.now, clock.day, clock.today, clock.time, clock.longdate


@loop(seconds=15)
async def change_status():
    await bot.wait_until_ready()
    await clock()
    activity = discord.Game(name=f'{clock.time} {clock.day}, {clock.today}')
    await bot.change_presence(status=discord.Status.online, activity=activity)


@bot.event
async def on_ready():
    global now
    now = datetime.now()
    print(f"We have logged in as {bot.user}")
    print(f'Client ID = {bot.user.id}')
    print(f'Discord version = {discord.__version__}')
    print(f'Server name = {bot.get_guild(135799278336475136)}')
    print(f'Users = {bot.get_guild(135799278336475136).member_count}')
    print(f'Status set to OnLine. Set activity to "Playing {clock.time} {clock.day}, {clock.today}"')
    channel = bot.get_channel(705808157863313468)
    print(f'We are in {channel}')
    await channel.send("I'm Online! Type help for all commands.")


@bot.event
async def on_member_join(member):
    print(f'{member.name} has joined')
    await member.add_roles(discord.utils.get(member.guild.roles, name='Member'))
    await bot.get_channel(705808157863313468).send(f'Welcome to Miami Nights, {member.mention}')


@bot.event
async def on_message(message):
    await clock()
    print(f'{clock.time} {message.author.display_name}({message.author}): {message.content}')

    for x in message.mentions:
        if x == bot.user:
            await message.channel.send(f'What do you want, {message.author.mention}?')

    await bot.process_commands(message)


@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello there, {ctx.author.mention}!')


@bot.command()
async def ping(ctx):
    print(bot.latency)
    x = f'{bot.latency:.3f}'
    x = float(x) * 1000
    x = int(x)
    x = f'{x} ms'
    await ctx.send(f'pong, {x}')


@bot.command()
async def time(ctx):
    await clock()
    await ctx.send(f"It's {clock.time}. Today is {clock.longdate}")


@bot.command()
async def roll(ctx):
    await ctx.send(f'{ctx.author.name} rolled {randrange(101)}')


@bot.command()
async def img(ctx):
    await ctx.send(file=discord.File('kroos.jpg'))


@bot.command()
async def roles(ctx):
    for x in ctx.guild.roles:
        if x == '@everyone':
            continue
        await ctx.send(f'{x.name}')


@bot.command()
async def role(ctx):
    await ctx.send(f'')


@bot.command()
async def simp(ctx):
    user = ctx.message.author
    role = discord.utils.get(user.guild.roles, name='Simp')
    if role in user.roles:
        await user.remove_roles(role)
        await ctx.send(f'{user.display_name} is not a {role} anymore')
    else:
        await user.add_roles(role)
        await ctx.send(f'{user.display_name} is a {role}')


@bot.command()
async def bonk(ctx, member):
    if ctx.message.author == ctx.guild.owner:
        await ctx.send(f'{member} bonked by {ctx.guild.owner.display_name}')
    else:
        await ctx.send(f"You can't do that bud")


# @bot.event # caches all errors
# async def on_command_error(ctx, error):
#     if isinstance(error, commands.MissingRequiredArgument):
#         await ctx.send(f'Who do you want me to Bonk?')


@bonk.error # caches errors for bonk command
async def bonk_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'Who do you want me to Bonk?')


@bot.command()
async def stats(ctx):
    uptime = datetime.now() - now
    await ctx.send(f'```\n{bot.user.display_name}\n'
                   f'Mem Usage = tbd\n'
                   f'Uptime = {str(uptime).split(".", 2)[0]}\n'
                   f'Server = {bot.get_guild(135799278336475136)}\n'
                   f'Users = {bot.get_guild(135799278336475136).member_count}\n'
                   f'Version = {discord.__version__}\n```')


@bot.command()
async def info(ctx):
    await ctx.send('```\nList of commands:\n'
                               '/info - displays this list\n'
                               '/time - displays current time\n'
                               '/ping - displays delay\n'
                               '/hello - greets user\n'
                               '/img - displays kroos.img\n'
                               '/roll - \n'
                               '/roles - \n'
                               '/role - \n'
                               '/simp - \n'
                               '/bonk - \n'
                               '/stats - \n'
                               'Bot is still in developement. More functions to come soon!```')


change_status.start()
bot.run(TOKEN)
