import discord
import time
import asyncio
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
from discord import Member
from discord.ext import commands
from discord.ext.commands import Bot
from discord import activity
from discord import state
from discord import client
from discord import enums
style.use("fivethirtyeight")

client = discord.Client()
# with open('config.json') as cfg_file:
#     print(f"> config loaded")

#     cfg = json.load(cfg_file)
OwnerID = 379400007410909186
Nick = 269946726918389770


def community_report(guild):
	online = 0
	idle = 0
	offline = 0

	for m in guild.members:
		if str(m.status) == "online":
			online += 1
		if str(m.status) == "offline":
			offline += 1
		else:
			idle += 1

	return online, idle, offline

async def user_metrics_background_task():
	await client.wait_until_ready()
	global kosmiccrew_guild
	kosmiccrew_guild = client.get_guild(269947224023105536)
	while not client.is_closed():
		try:
			online, idle, offline = community_report(kosmiccrew_guild)
			with open("usermetrics.csv","a") as f:
				f.write(f"{int(time.time())},{online},{idle},{offline}\n")

			df = pd.read_csv("usermetrics.csv", names=['time', 'online', 'idle', 'offline'])
			df['date'] = pd.to_datetime(df['time'],unit='s')
			df['total'] = df['online'] + df['offline'] + df['idle']
			df.drop("time", 1,  inplace=True)
			df.set_index("date", inplace=True)

			plt.clf()
			df['online'].plot()
			plt.legend()
			plt.savefig("online.png")
			await asyncio.sleep(1800)

		except Exception as e:
			print(str(e))
			await asyncio.sleep(1800)

@client.event  # event decorator/wrapper
async def on_ready():
	global kosmiccrew_guild
	await client.wait_until_ready()
	await client.change_presence(activity=discord.Activity(type=2, name='typ.help'))
	print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
	global kosmiccrew_guild
	print(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")

	if "typ.help" == message.content.lower():
		embed = discord.Embed(title="ThatsYourProblem Help Menu", description="The commands for ThatsYourProblem are listed here.  [🐦 My Twitter](https://twitter.com/RealIm2Epic4U)  [📺 My Twitch](https://twitch.tv/realim2epic4u)  [🎵 My Spotify](https://open.spotify.com/user/s41fdjzscxb28te73ei9lk9bb?si=9T5VmoynSH2qoCGOy-KHEg)", colour=discord.Colour.blue())
		embed.add_field(name='Autoreponder', value='Automatically responds to messages.', inline=True)
		embed.add_field(name='typ.membercount', value='Gets the number of members in the server.', inline=True)
		embed.add_field(name='typ.report', value='Gets a list of how many people are online and how many people have which statuses.')
		embed.set_footer(text='Contact <@379400007410909186> is there is a bug with this bot.', icon_url='https://cdn.discordapp.com/avatars/379400007410909186/a_264e49cb370914994eda22c49ed2aa96.gif')
		embed.set_thumbnail(url='https://cdn.discordapp.com/avatars/379400007410909186/a_264e49cb370914994eda22c49ed2aa96.gif')
		embed.set_author(name=message.author, icon_url=message.author.avatar_url)
		await message.channel.send(content=None, embed=embed)

	elif "typ.membercount" == message.content.lower():
		await message.channel.send(f"```py\n{kosmiccrew_guild.member_count}```")

	elif "typ.logout" == message.content.lower():
		if message.author.id == OwnerID or Nick:
			await message.channel.send(f"Logging out...")
			await client.logout()
		else:
			await message.channel.send(f"You do not have permission to use this command, only the owner of the bot can run this command.")

	elif "typ.report" == message.content.lower():
		online, idle, offline = community_report(kosmiccrew_guild)
		await message.channel.send(f"```py\nOnline: {online}\nIdle/busy/dnd: {idle}\nOffline: {offline}```")
		file = discord.File("online.png", filename="online.png")
		await message.channel.send("online.png", file=file)

	elif "that's your problem" == message.content.lower():
		await message.channel.send(f"no u")

client.loop.create_task(user_metrics_background_task())
client.run(os.getenv('TOKEN'))