import discord
import asyncio
import uvicorn
from fastapi import FastAPI, Body
from models import RequestData, DELETE
from utils import decode_base64_to_file
from config import TOKEN
from events import setup_event_handlers


app = FastAPI()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.dm_messages = True
client = discord.Client(intents=intents)

setup_event_handlers(client)

@app.post("/discord-telegram/")
async def receive_from_telegram(
        chat_id: int,
        data: RequestData = Body(...)
):
    channel = client.get_channel(chat_id)
    if not channel:
        return {"status": "failed", "reason": "channel not found"}

    message_content = f"**Author:** {data.author.name} ({data.author.tag})\n**Channel:** {data.channel}\n{data.message.text}"
    files = []
    for attachment in data.message.attachments:
        file = decode_base64_to_file(attachment.data, attachment.type)
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
        print("✅ Message deleted!")
    except discord.NotFound:
        print("❌ Message not found!")
    except discord.Forbidden:
        print("❌ No permission to delete message! !")
    except discord.HTTPException:
        print("❌ An error occurred while deleting message! !")



async def main():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await asyncio.gather(
        server.serve(),
        client.start(TOKEN)
    )

asyncio.run(main())
