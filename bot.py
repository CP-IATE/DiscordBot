import discord
import asyncio
import uvicorn
import aiohttp
import io
import base64
from dotenv import dotenv_values
from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import List, Literal



cfg = dotenv_values("config.env")

app = FastAPI()

TOKEN = cfg.get("TOKEN")
TARGET_API_URL = cfg.get("TARGET_API_URL")

class Author(BaseModel):
    tag: str
    name: str

class Attachment(BaseModel):
    type: Literal["image", "archive"]  # Додати інші типи
    data: str           #List[int]

class Message(BaseModel):
    text: str
    attachments: List[Attachment] = [] # Не обов'язково

class RequestData(BaseModel):
    platform: Literal["telegram", "discord"]
    author: Author
    message: Message

class DELETE(BaseModel):
    message_id: int

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

@app.post("/discord/")
async def send_to_api(
    data: RequestData = Body(...)
):
    async with aiohttp.ClientSession() as session:
        payload = {
            "platform": data.platform,
            "author" : {
                "tag": data.author.tag,
                "name": data.author.name
            },
            "message": {
                "text": data.message.text,
                "attachments": [{"type": att.type, "data": att.data} for att in data.message.attachments]
            }
        }
        async with session.get(TARGET_API_URL, json=payload) as response:
            result = await response.json()
            return {"status": "sent", "response": result}

@app.get("/discord/")
async def send_to_discord(
    chat_id: int,
    data: RequestData = Body(...)
):
    channel = client.get_channel(chat_id)
    if not channel:
        return {"status": "failed", "reason": "channel not found"}

    message_content = f"**Автор:** {data.author.name} ({data.author.tag})\n{data.message.text}"

    files = []
    for attachment in data.message.attachments:
       if attachment.type == "image":
           image_bytes = base64.b64decode(attachment.data)
           file = discord.File(io.BytesIO(image_bytes), filename="image.png") #filename=attachment.filename
           files.append(file)

    await channel.send(content=message_content, files=files if files else None)
    return {"status": "sent"}


@app.delete("/discord/")
async def delete_message(
    chat_id: int,
    delete: DELETE
):
    """Видаляє повідомлення за ID"""
    channel = client.get_channel(chat_id)
    if not channel:
        return {"status": "failed", "reason": "channel not found"}

    try:
        message = await channel.fetch_message(delete.message_id)
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
