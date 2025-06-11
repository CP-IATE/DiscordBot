from utils import encode_file_to_base64
from models import RequestData, Author, Message, Attachment
from config import TARGET_API_URL, TARGET_API_URL2
import aiohttp
from fastapi import Body
import discord
from DMhandler import process_dm_message, handle_post_content

async def send_message_to_telegram(
    data: RequestData = Body(...)
):
    async with aiohttp.ClientSession() as session:
        payload = {
            "platform": data.platform,
            "channel": data.channel,
            "author" : {
                "tag": data.author.tag,
                "name": data.author.name
            },
            "message": {
                "text": data.message.text,
                "attachments": [{"type": att.type, "data": att.data} for att in data.message.attachments]
            }
        }
        async with session.post(TARGET_API_URL2, json=payload) as response:
            result = await response.json()
            return {"status": "sent", "response": result}



def setup_event_handlers (client):
    @client.event
    async def on_ready() -> None:
        print(f"Bot {client.user} is running...!")

    @client.event
    async def on_message(message) -> None:
        if message.author == client.user:
            return

        if isinstance(message.channel, discord.DMChannel):
            if message.content == "!post":
                await process_dm_message(message)
            else:
                await handle_post_content(message)
            return

        """ probably unnecessary part"""
        if message.content.strip():
            print(f"[{message.guild.name} | {message.channel.name}] {message.author}: {message.content}")

        file_mime_dict = {}
        for attachment in message.attachments:
            print(f"📂 File received: {attachment.filename} ({attachment.size} bytes)\n")
            file_bytes = await attachment.read()
            base64_data = encode_file_to_base64(file_bytes)
            filename = attachment.filename
            file_mime_dict[base64_data] = filename

        request_data = RequestData(
            platform="discord",
            channel= message.channel.name,
            author=Author(tag=message.author.name, name=message.author.display_name),
            message=Message(
                text=message.content,
                attachments=[Attachment(type=mime, data=file) for file, mime in file_mime_dict.items()]
            )
        )
        await send_message_to_telegram(request_data)
