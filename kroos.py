import discord
from datetime import datetime
import asyncio

TOKEN = None

client = discord.Client()
# id = 135799278336475136


async def clock():
    clock.now = datetime.now()
    clock.day = datetime.today().strftime('%a')
    clock.today = clock.now.strftime('%d-%b-%Y')
    clock.time = clock.now.strftime('%H:%M')
    clock.longdate = clock.now.strftime('%A, %d of %B, %Y')
    return clock.now, clock.day, clock.today, clock.time, clock.longdate


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    print(f'Client ID = {client.user.id}')
    print(f'Discord version = {discord.__version__}')
    print(f'Server name = {client.get_guild(135799278336475136)}')
    print(f'Users = {client.get_guild(135799278336475136).member_count}')
    channel = client.get_channel(705808157863313468)
    await channel.send("I'm Online! Type help for all commands.")


async def change_status():
    await client.wait_until_ready()
    while True:
        await clock()
        client.activity = discord.Game(name=f'{clock.time} {clock.day}, {clock.today}')
        await client.change_presence(status=discord.Status.online, activity=client.activity)
        await asyncio.sleep(5)


@client.event
async def on_member_join(member):
    print(f'{member.name} has joined')
    await client.get_channel(705808157863313468).send(f'Welcome to Miami Nights, {member.mention}')


@client.event
async def on_message(message):
    await clock()
    print(f'{clock.time} {message.author.display_name}({message.author}): {message.content}')
    if message.author == client.user:
        return

    if message.content.lower() == 'hello':
        await message.channel.send(f'Hello, {message.author.display_name}!')

    if message.content.lower() == 'ping':
        x = f'{client.latency:.3f}'
        x = float(x)*1000
        x = int(x)
        x = f'{x} ms'
        await message.channel.send(f'pong, {x}')

    if message.content.lower() == 'time':
        await clock()
        await message.channel.send(f"It's {clock.time}. Today is {clock.longdate}")

    if message.content.lower() == 'help':
        await message.channel.send('```list of commands:\n'
                                   'help - displays this list\n'
                                   'time - displays current time\n'
                                   'ping - displays delay between your pc and discord server\n'
                                   'hello - greets user\n'
                                   'img - displays kroos.img\n'
                                   'Bot is still in developement. More functions to come soon!```')

    for x in message.mentions:
        if x == client.user:
            await message.channel.send(f'What do you want, {message.author.mention}?')

    if message.content.lower() == 'img':
        await message.channel.send(file=discord.File('kroos.jpg'))


client.loop.create_task(change_status())
client.run(TOKEN)
