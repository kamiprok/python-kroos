import discord
from datetime import datetime
from discord.ext import commands
from discord.ext.tasks import loop
import os

TOKEN = os.environ['token']

bot = commands.Bot(command_prefix='/')


async def clock():
    clock.now = datetime.now()
    clock.day = datetime.today().strftime('%a')
    clock.today = clock.now.strftime('%d-%b-%Y')
    clock.time = clock.now.strftime('%H:%M')
    clock.longdate = clock.now.strftime('%A, %d of %B, %Y')
    return clock.now, clock.day, clock.today, clock.time, clock.longdate


@loop(seconds=5)
async def change_status():
    await bot.wait_until_ready()
    while True:
        await clock()
        bot.activity = discord.Game(name=f'{clock.time} {clock.day}, {clock.today}')
        await bot.change_presence(status=discord.Status.online, activity=bot.activity)


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    print(f'Client ID = {bot.user.id}')
    print(f'Discord version = {discord.__version__}')
    print(f'Server name = {bot.get_guild(135799278336475136)}')
    print(f'Users = {bot.get_guild(135799278336475136).member_count}')
    channel = bot.get_channel(705808157863313468)
    print(f'We are in {channel}')
    await channel.send("I'm Online! Type help for all commands.")


@bot.event
async def on_member_join(member):
    print(f'{member.name} has joined')
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
async def img(ctx):
    await ctx.send(file=discord.File('kroos.jpg'))


@bot.command()
async def commands(ctx):
    await ctx.send('```list of commands:\n'
                               '/commands - displays this list\n'
                               '/time - displays current time\n'
                               '/ping - displays delay between your pc and discord server\n'
                               '/hello - greets user\n'
                               '/img - displays kroos.img\n'
                               'Bot is still in developement. More functions to come soon!```')


change_status.start()
bot.run(TOKEN)
