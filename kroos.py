import discord
from datetime import datetime
from discord.ext import commands
from discord.ext.tasks import loop
import os
import pytz
from random import randrange, choice
from asyncio import sleep
from pymongo import MongoClient, errors
import logging
import praw

# logging.basicConfig(level=logging.INFO)  # DEBUG

# bot
TOKEN = os.environ['token']

bot = commands.Bot(command_prefix='/', description='Kroos Bot')
bot.remove_command('help')


# db
MongoDBConnectionString = os.environ['MongoDBConnectionString']

try:
    print('Connecting to DB')
    client = MongoClient(MongoDBConnectionString, serverSelectionTimeoutMS=10000)
    client.server_info()
except errors.ServerSelectionTimeoutError:
    print('DB connection error')
except errors.OperationFailure:
    print('DB authentication failed')
print('DB connection established')

db = client.MongoDB

# reddit
user_agent = os.environ['user_agent']
client_id = os.environ['client_id']
client_secret = os.environ['client_secret']


def reddit_start():
    reddit = praw.Reddit(user_agent=user_agent,
                        client_id=client_id,
                        client_secret=client_secret)
    return reddit


# time


async def clock():
    tz = pytz.timezone('Europe/Warsaw')
    clock.now = datetime.now().astimezone(tz)
    clock.day = datetime.today().astimezone(tz).strftime('%a')
    clock.today = clock.now.strftime('%d-%b-%Y')
    clock.time = clock.now.strftime('%H:%M')
    clock.longdate = clock.now.strftime('%A, %d of %B, %Y')
    return clock.now, clock.day, clock.today, clock.time, clock.longdate


# events


@bot.event
async def on_ready():
    global now
    global owner_name
    global server_name
    global channel_general
    global reddit
    owner_name = bot.get_guild(135799278336475136).owner
    server_name = bot.get_guild(135799278336475136)
    channel_general = bot.get_channel(705808157863313468)
    now = datetime.now()
    reddit = reddit_start()
    print(f"We have logged in as {bot.user}")
    print(f'Client ID = {bot.user.id}')
    print(f'Discord version = {discord.__version__}')
    print(f'Server name = {server_name}')
    print(f'Server owner = {owner_name.display_name}')
    print(f'Users = {server_name.member_count}')
    print(f'Status set to OnLine. Set activity to "Playing {clock.time} {clock.day}, {clock.today}"')
    print(f'We are in {channel_general}')
    print(f'Reddit connected: {reddit.read_only}')
    await channel_general.send("I'm Online! Type /help for list of commands")


@bot.event
async def on_member_join(member):  # dm me when new member joins, dm member with /help
    print(f'{member.name} has joined')
    await owner_name.send(f'{member.display_name} ({member}) has joined {server_name}. Total users: {server_name.member_count}')
    await member.add_roles(discord.utils.get(member.guild.roles, name='Member'))
    await channel_general.send(f'Welcome to Miami Nights, {member.mention}')
    await member.send(f'Welcome to Miami Nights, {member.mention}\n'
                      f'Type /help for list of commands')


@bot.event
async def on_message(message):
    await clock()
    # disabled for debug logging
    # print(f'{clock.time} {message.author.display_name}({message.author}): {message.content}')
    for x in message.mentions:
        if x == bot.user:
            await message.channel.send(f'What do you want, {message.author.mention}?')
    bad_words = ['kurwa']
    for i in bad_words:
        if i in message.content.lower():
            await message.delete()
            await message.channel.send(f'Language, {message.author.mention}!')
    await bot.process_commands(message)


# loops


@loop(seconds=10)
async def change_status():
    await bot.wait_until_ready()
    await clock()
    activity = discord.Game(name=f'{clock.time} {clock.day}, {clock.today}')
    db.kroos.update_many({'_id': 2}, {'$set': {'bot_activity': str(activity)}, '$inc': {'loop': 1}})
    await bot.change_presence(status=discord.Status.online, activity=activity)


helper = 'helper'  # helper string for random_message loop so it won't print the same msg twice in a row


@loop(seconds=3600)  # @loop(seconds=randrange(900, 1800, 300))  # sets random once on start of the loop, should be different every loop
async def random_message():
    global helper
    await bot.wait_until_ready()
    if random_message.current_loop == 0:
        return
    else:
        today = datetime.today().strftime('%A')
        emoji = discord.utils.get(bot.get_guild(135799278336475136).emojis, name='donkey')
        messages = ['Type /help for list of commands', f'Today is {today}', "What's up?", "Stay hydrated", f'Please obey the server rules {emoji}']
        while True:
            rand_msg = choice(messages)
            if helper != rand_msg:
                helper = rand_msg
                break
        db.kroos.update_one({'_id': 3}, {'$set': {'last_message': rand_msg}, '$inc': {'loop': 1}})
        await bot.get_channel(705808157863313468).send(f'{rand_msg}')


# commands


@bot.command()
async def hello(ctx):
    resp = ['Hello there', 'Hi', 'Sup', 'Hello', "What's up"]
    rand_resp = choice(resp)
    await ctx.send(f'{rand_resp}, {ctx.author.mention}!')


@bot.command()
async def ping(ctx):
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
async def roll(ctx):
    await ctx.send(f'{ctx.author.display_name} rolled {randrange(101)}')


@bot.command()  # user must be valid username
async def status(ctx, user: discord.Member):
    if user == ctx.message.author:
        await ctx.send(f'You are {ctx.message.author.status}')
    elif user == bot.user:
        await ctx.send(f"I'm Online")
    else:
        await ctx.send(f'{user.display_name} is {user.status}')


@status.error  # caches errors for status command
async def status_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Who's status to check? (argument required)")


@bot.command()
async def goodbot(ctx):
    emoji = discord.utils.get(ctx.guild.emojis, name='pramblush')
    db.kroos.find_one_and_update({'_id': 1}, {'$inc': {'blushed': 1}})
    await ctx.send(emoji)  # it should react to command but for now just sends emoji


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


# old roles command
# @bot.command()
# async def roles(ctx):
#     for role in ctx.guild.roles:
#         if str(role) == '@everyone':
#             continue
#         else:
#             await ctx.send(f'{role.name}')


# new roles command
@bot.command()
async def roles(ctx):
    await ctx.send('Use /role {role_name} command to pick one of 3 roles:\n\nKnight\nCaptain\nBaron')


@bot.command()
async def role(ctx, affirmation):
    if affirmation in ('Mod', 'Admin'):
        await ctx.send('You wish buddy')
        return
    user = ctx.message.author
    roles_names = ['Knight', 'Captain', 'Baron']  # literals for now
    if affirmation in roles_names:
        affirmation = discord.utils.get(user.guild.roles, name=affirmation)
    else:
        await ctx.send(f'Pick from these 3 only: Knight, Captain, Baron')  # literals for now
        return
    if affirmation in user.roles:
        await user.remove_roles(affirmation)
        await ctx.send(f'{user.display_name} is no longer a {affirmation.name}')
        return
    roles_objects = []
    user_roles = []
    for i in roles_names:
        roles_objects.append(discord.utils.get(user.guild.roles, name=i))
    for roles in user.roles:
        user_roles.append(roles)
    for i in roles_objects:
        if i in user_roles:
            user_roles.remove(i)
    user_roles.append(affirmation)
    await user.edit(roles=user_roles)
    await ctx.send(f'{user.display_name} is now a {affirmation.name}')


# @bot.command()  # good idea but it removes warns
# async def norole(ctx):
#     user = ctx.message.author
#     role = []
#     role.append(discord.utils.get(user.guild.roles, name='Member'))
#     await user.edit(roles=role)
#     await ctx.send(f'Back to square one huh')


@role.error  # caches errors for role command
async def role_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Argument required. Type /roles for more info')


@bot.command()
async def owner(ctx):
    if ctx.message.author == owner_name:
        await ctx.send(f"That's you {owner_name.mention}")
    else:
        await ctx.send(f'{owner_name.display_name} is this server owner')


@bot.command()
async def karma(ctx, user):
    try:
        reddit = reddit_start()
        username = reddit.redditor(user)
        total_karma = username.link_karma + username.comment_karma
        await ctx.send(f"{user}'s karma: {total_karma}")
    except:
        await ctx.send(f'User {user} not found on reddit')


@karma.error  # caches errors for karma command
async def karma_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Who's karma to check? (argument required)")


@bot.command()
async def reddit(ctx, sub: str):
    try:
        submissions = reddit.subreddit(sub).top(time_filter='day', limit=1)
        for submission in submissions:
            shortlink = submission.shortlink
        await ctx.send(f'Top post today on r/{reddit.subreddit(sub).display_name}:\n')
        await ctx.send(shortlink)
    except:
        await ctx.send('Enter valid subreddit name as argument')


@reddit.error  # caches errors for reddit command
async def reddit_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Enter subreddit name as argument")


@bot.command()
async def stats(ctx):
    uptime = datetime.now() - now
    blushed = db.kroos.find_one({'_id': 1})
    blushed_val = blushed['blushed']
    await ctx.send(f'```\n{bot.user.display_name}\n'
                   f'Uptime = {str(uptime).split(".", 2)[0]}\n'
                   f'Server = {server_name}\n'
                   f'Users = {server_name.member_count}\n'
                   f'Version = {discord.__version__}\n'
                   f'Blushed = {blushed_val} times```')


@bot.command()
async def help(ctx):
    embed = discord.Embed(title='Kroos')
    embed.add_field(name='List of commands:', value='/help - display this list\n'
                                '/hello - random greeting\n'
                                '/ping - display delay\n'
                                '/time - display current time\n'
                                '/img - display image\n'
                                '/roll - roll dice 0-100\n'
                                '/roles - see server roles\n'
                                '/role - assign one of 3 roles to yourself\n'
                                '/simp - assign Simp role to yourself\n'
                                '/karma {reddit user} - reddit user karma\n'
                                '/reddit {subreddit} - top post for today\n'
                                '/status {user} - check user status\n'
                                '/stats - display server statistics\n'
                                '/owner - display server owner\n'
                                '/goodbot - prise Kroos!\n\n'
                                'Bot is still in development. More functions to come soon!')
    await ctx.send(embed=embed)


@bot.event  # caches all errors
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f'No such command. Type /help for list of commands')
    if isinstance(error, commands.MissingRole):
        await ctx.send(f"You can't do that bud")


# admin


@bot.command()
@commands.has_role('Admin' or 'Mod')
async def warn(ctx, user: discord.Member, seconds: int):
    role = discord.utils.get(user.guild.roles, name='Warned')
    await user.add_roles(role)
    await ctx.send(f'{user.display_name} warned for {seconds} seconds')
    await sleep(seconds)
    await user.remove_roles(role)
    await ctx.send(f"{user.display_name}'s warn is over")


@warn.error  # caches errors for warn command
async def warn_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('/warn {user} {seconds}')


@bot.command()
@commands.has_role('Admin' or 'Mod')
async def bonk(ctx, user: discord.Member, seconds: int):
    user_roles = []
    for role in user.roles:
        user_roles.append(role)
    muted = []
    muted.append(discord.utils.get(user.guild.roles, name='Muted'))
    await user.edit(roles=muted)
    await ctx.send(f'{user.display_name} bonked for {seconds} seconds')
    await sleep(seconds)
    await user.edit(roles=user_roles)
    await ctx.send(f"{user.display_name}'s timeout is over")


@bot.command()
@commands.has_role('Admin' or 'Mod')
async def unbonk(ctx, user: discord.Member):
    role = []
    role.append(discord.utils.get(user.guild.roles, name='Member'))
    await user.edit(roles=role)
    await ctx.send(f'{user.display_name} force unbonked. Temp role Member added until bonk time runs out')


@bonk.error  # caches errors for bonk command
async def bonk_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('/bonk {user} {seconds}')


@bot.command()
@commands.has_role('Admin')
@commands.has_permissions(administrator=True)
async def task(ctx, task: str):  # use "" to parse 2 words as one string
    if task in ('change status', '1'):
        await ctx.message.author.send(f'{change_status.get_task()}')
    elif task in ('random message', '2'):
        await ctx.message.author.send(f'{random_message.get_task()}')
    else:
        await ctx.message.author.send(f'{change_status.get_task()}\n'
                                      f'{random_message.get_task()}')


@bot.command()
@commands.has_role('Admin')
@commands.has_permissions(administrator=True)
async def stop(ctx, task: str):
    if task in ('change status', '1'):
        change_status.cancel()
        await ctx.send(f'Change status background task stopped')
    elif task in ('random message', '2'):
        random_message.cancel()
        await ctx.send(f'Random message background task stopped')
    else:
        change_status.cancel()
        random_message.cancel()
        await ctx.send(f'All background tasks stopped')


@bot.command()
@commands.has_role('Admin')
@commands.has_permissions(administrator=True)
async def start(ctx, task: str):
    if task in ('change status', '1'):
        change_status.start()
        await ctx.send(f'Change status background task started')
    elif task in ('random message', '2'):
        random_message.start()
        await ctx.send(f'Random message background task started')
    else:
        change_status.start()
        random_message.start()
        await ctx.send(f'All background tasks started')


@bot.command()
@commands.has_role('Admin')
@commands.has_permissions(administrator=True)
async def restart(ctx, task: str):
    if task in ('change status', '1'):
        change_status.restart()
        await ctx.send(f'Change status background task restarted')
    elif task in ('random message', '2'):
        random_message.restart()
        await ctx.send(f'Random message background task restarted')
    else:
        change_status.restart()
        random_message.restart()
        await ctx.send(f'All background tasks restarted')


@bot.command()
@commands.has_role('Admin')
@commands.has_permissions(administrator=True)
async def load(ctx, module: str):
    bot.load_extension(module)
    await ctx.send(f'Module {module} loaded')


@bot.command()
@commands.has_role('Admin')
@commands.has_permissions(administrator=True)
async def unload(ctx, module: str):
    bot.unload_extension(module)
    await ctx.send(f'Module {module} unloaded')


@bot.command()
@commands.has_role('Admin')
@commands.has_permissions(administrator=True)
async def reload(ctx, module: str):
    bot.unload_extension(module)
    bot.load_extension(module)
    await ctx.send(f'Module {module} reloaded')


@bot.command()
@commands.has_role('Admin')
@commands.has_permissions(administrator=True)
async def shutdown(ctx):
    await ctx.send(f'Shutting down')
    await ctx.bot.logout()


bot.load_extension('cogs.custom')
change_status.start()
random_message.start()
bot.run(TOKEN)
