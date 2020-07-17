import discord
from datetime import datetime
from discord.ext import commands
from discord.ext.tasks import loop
import os
import pytz
from random import randrange, choice
from asyncio import sleep
import json

TOKEN = os.environ['token']

bot = commands.Bot(command_prefix='/', description='Kroos Bot')
bot.remove_command('help')

# init for json file to store variables
# data = {'blush': 0}
# with open('data.json', 'w') as f:
#     json.dump(data, f)


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


@loop(seconds=randrange(600, 3600))
async def random_message():
    await bot.wait_until_ready()
    if random_message.current_loop == 0:
        # await bot.get_channel(705808157863313468).send(f"Welcome to {bot.get_guild(135799278336475136)}!")
        return
    else:
        today = datetime.today().strftime('%A')
        emoji = discord.utils.get(bot.get_guild(135799278336475136).emojis, name='donkey')
        messages = ['Type /help for list of commands', f'Today is {today}', "I'm Kroos!", "I'm Online!", f'Please obey the server rules {emoji}']
        rand_msg = choice(messages)
        await bot.get_channel(705808157863313468).send(f'{rand_msg}')


@bot.command()
@commands.has_role('Admin')
async def botstatus(ctx):
    await ctx.message.author.send(f'{change_status.get_task()}\n'
                                  f'{random_message.get_task()}')


@bot.command()
@commands.has_role('Admin')
async def restart(ctx):
    change_status.restart()
    random_message.restart()
    await ctx.send(f'Background tasks restarted.')


@bot.event
async def on_ready():
    global now
    global owner_name
    global server_name
    global channel_general
    owner_name = bot.get_guild(135799278336475136).owner
    server_name = bot.get_guild(135799278336475136)
    channel_general = bot.get_channel(705808157863313468)
    now = datetime.now()
    print(f"We have logged in as {bot.user}")
    print(f'Client ID = {bot.user.id}')
    print(f'Discord version = {discord.__version__}')
    print(f'Server name = {server_name}')
    print(f'Server owner = {owner_name.display_name}')
    print(f'Users = {server_name.member_count}')
    print(f'Status set to OnLine. Set activity to "Playing {clock.time} {clock.day}, {clock.today}"')
    print(f'We are in {channel_general}')
    await channel_general.send("I'm Online! Type /help for list of commands.")


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
async def roll(ctx):
    await ctx.send(f'{ctx.author.display_name} rolled {randrange(101)}')


@bot.command()  # user must be valid username
async def status(ctx, user: discord.Member):
    if user == ctx.message.author:
        await ctx.send(f'You are {ctx.message.author.status}')
    elif user == bot.user:
        await ctx.send(f"I'm Online.")
    else:
        await ctx.send(f'{user.display_name} is {user.status}')


@status.error  # caches errors for status command
async def status_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Who's status to check? (argument required)")


@bot.command()
async def goodbot(ctx):
    with open('data.json', 'r') as f:
        data = json.load(f)
    data['blush'] += 1
    with open('data.json', 'w') as f:
        json.dump(data, f)
    emoji = discord.utils.get(ctx.guild.emojis, name='pramblush')
    await ctx.send(emoji)  # it should react to command but for now just sends emoji


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
        await ctx.send('Argument required. Type /roles for more info.')


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


@bot.command()  # old command to simply add Muted role on top of other roles
@commands.has_role('Admin' or 'Mod')  # rewritten to warn so you can warn members
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
    await ctx.send(f'{user.display_name} force unbonked. Temp role Member added until bonk time runs out.')


@bonk.error  # caches errors for bonk command
async def bonk_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('/bonk {user} {seconds}')


@bot.command()
async def owner(ctx):
    if ctx.message.author == owner_name:
        await ctx.send(f"That's you {owner_name.mention}")
    else:
        await ctx.send(f'{owner_name.display_name} is this server owner')


@bot.command()
async def stats(ctx):
    uptime = datetime.now() - now
    with open('data.json') as f:
        data = json.load(f)
    await ctx.send(f'```\n{bot.user.display_name}\n'
                   f'Mem Usage = tbd\n'
                   f'Uptime = {str(uptime).split(".", 2)[0]}\n'
                   f'Server = {server_name}\n'
                   f'Users = {server_name.member_count}\n'
                   f'Version = {discord.__version__}\n'
                   f'Blushed = {data.get("blush")} times```')


@bot.command()
async def help(ctx):
    await ctx.send('```\nList of commands:\n'
                                '/help - display this list\n'
                                '/hello - greet yourself\n'
                                '/ping - display delay\n'
                                '/time - display current time\n'
                                '/img - display image\n'
                                '/roll - roll dice 0-100\n'
                                '/roles - see server roles\n'
                                '/role - assign one of 3 roles to yourself\n'
                                '/simp - assign Simp role to yourself\n'
                                '/status {user} - check user status\n'
                                '/stats - display server statistics\n'
                                '/owner - display server owner\n'
                                '/goodbot - prise Kroos!\n'
                                'Bot is still in development. More functions to come soon!```')


@bot.event  # caches all errors
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f'No such command. Type /help for list of commands.')
    if isinstance(error, commands.MissingRole):
        await ctx.send(f"You can't do that bud")


change_status.start()
random_message.start()
bot.run(TOKEN)
