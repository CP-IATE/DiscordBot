import discord
import asyncio
import uvicorn
import aiohttp
from dotenv import dotenv_values
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Literal



cfg = dotenv_values("config.env")

app = FastAPI()

TOKEN = cfg.get("TOKEN")
TARGET_API_URL = cfg.get("TARGET_API_URL")

class Message(BaseModel):
    chat_id : int
    text: str

class DELETE(BaseModel):
    chat_id : int
    message_id: int


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)




@app.post("/discord/")
async def send_to_api(message: Message):
    """Відправляє запит на інше API"""
    async with aiohttp.ClientSession() as session:
        payload = {"chat_id": message.chat_id, "text": message.text}
        async with session.get(TARGET_API_URL, json=payload) as response:
            result = await response.json()
            return {"status": "sent", "response": result}

@app.get("/discord/")
async def send_to_discord(message:Message):
    channel = client.get_channel(message.chat_id)
    if channel:
        await channel.send(message.text)
        return {"status": "sent"}
    return {"error": "Channel not found"}

@app.delete("/discord/")
async def delete_message(message: DELETE):
    """Видаляє повідомлення за ID"""
    channel = client.get_channel(message.chat_id)
    try:
        message = await channel.fetch_message(message.message_id)
        await message.delete()
        print("✅ Повідомлення видалено!")
    except discord.NotFound:
        print("❌ Повідомлення не знайдено!")
    except discord.Forbidden:
        print("❌ У мене немає прав на видалення!")
    except discord.HTTPException:
        print("❌ Сталася помилка при видаленні!")


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
        #if message.content.strip():
        #    file_bytes = await attachment.read()

async def main():
    # Запускаємо FastAPI у фоновому режимі
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)


    await asyncio.gather(
        server.serve(),
        client.start(TOKEN)
    )

asyncio.run(main())
