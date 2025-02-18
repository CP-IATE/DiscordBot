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

    # Виводимо повідомлення, якщо воно містить текст
    if message.content.strip():
        print(f"[{message.guild.name} | {message.channel.name}] {message.author}: {message.content}")

    for attachment in message.attachments:
        print(f"📂 Отримано файл: {attachment.filename} ({attachment.size} байт)\n")
        if message.content.strip():
            file_bytes = await attachment.read()

client.run(TOKEN)