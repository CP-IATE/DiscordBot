import discord

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.dm_messages = True
client = discord.Client(intents=intents)
