import discord
import requests
import asyncio
import uvicorn
from dotenv import dotenv_values
from fastapi import FastAPI
from pydantic import BaseModel



config = dotenv_values("config.env")

app = FastAPI()

TOKEN = config.get("TOKEN")

class Message(BaseModel):
    chat_id: int
    text: str

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)


@app.post("/send-to-discord/")
async def send_to_discord(message: Message):
    channel = client.get_channel(message.chat_id)
    if channel:
        await channel.send(message.text)
        return {"status": "sent"}
    return {"error": "Channel not found"}

@client.event
async def on_ready():
    print(f"Bot {client.user} is running...!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.strip():
        print(f"[{message.guild.name} | {message.channel.name}] {message.author}: {message.content}")

    for attachment in message.attachments:
        print(f"📂 Отримано файл: {attachment.filename} ({attachment.size} байт)\n")
        if message.content.strip():
            file_bytes = await attachment.read()

async def main():
    # Запускаємо FastAPI у фоновому режимі
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)

    # Запускаємо обидва сервіси одночасно
    await asyncio.gather(
        server.serve(),
        client.start(TOKEN)
    )

asyncio.run(main())

#client.run(TOKEN)
