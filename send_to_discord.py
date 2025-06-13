from discord import File
from bot import client
from utils import decode_base64_to_file
from models import Post
from dbContext import post_collection
from datetime import datetime
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
        async with session.post(TARGET_API_URL2, json=payload) as response:
            result = await response.json()
            return {"status": "sent", "response": result}
