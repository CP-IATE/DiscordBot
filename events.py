from utils import encode_file_to_base64
from models import RequestData, Author, Message, Attachment
from config import TARGET_API_URL, TARGET_API_URL2
import aiohttp
from fastapi import Body


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
        async with session.post(TARGET_API_URL, json=payload) as response:
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

        if message.content.strip():
            print(f"[{message.guild.name} | {message.channel.name}] {message.author}: {message.content}")

        files = []
        for attachment in message.attachments:
            print(f"📂 File received: {attachment.filename} ({attachment.size} bytes)\n")
            file_bytes = await attachment.read()
            base64_data = encode_file_to_base64(file_bytes)
            files.append(base64_data)

        request_data = RequestData(
            platform="discord",
            channel= message.channel.name,
            author=Author(tag=message.author.name, name=message.author.display_name),
            message=Message(
                text=message.content,
                attachments= [Attachment(type = "image", data=file) for file in files]
            )
        )
        await send_message_to_telegram(request_data)
        #print(f"📂 File: {attachment.filename} coded into Base64! - {base64_data}")