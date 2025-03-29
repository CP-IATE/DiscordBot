import discord
import asyncio
import uvicorn
import aiohttp
from fastapi import FastAPI, Body

from models import RequestData, DELETE
from utils import encode_file_to_base64, decode_base64_to_file
from config import TOKEN, TARGET_API_URL
from events import setup_event_handlers
app = FastAPI()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

setup_event_handlers(client)

@app.post("/discord-telegram/")
async def send_message_to_telegram(
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

@app.get("/discord-telegram/")
async def receive_message_from_telegram(
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
           file = decode_base64_to_file(attachment.data, "image.png")
           files.append(file)

    await channel.send(content=message_content, files=files if files else None)
    return {"status": "sent"}


@app.delete("/discord-telegram/")
async def delete_message_in_channel(
    chat_id: int,
    delete: DELETE
):
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

async def main():
    # Запускаємо FastAPI у фоновому режимі
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await asyncio.gather(
        server.serve(),
        client.start(TOKEN)
    )

asyncio.run(main())
