import discord
from dotenv import dotenv_values


config = dotenv_values("config.env")

TOKEN = config.get("TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True


client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Bot {client.user} is running...!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    print(f"[{message.guild.name} | {message.channel.name}] {message.author}: {message.content}")

client.run(TOKEN)