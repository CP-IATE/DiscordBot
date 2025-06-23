from models import RequestData, Post
from config import  TARGET_API_URL2, TARGET_API_URL3
import aiohttp
from fastapi import Body
#= Body(...)
async def send_message_to_telegram(
    data: Post = Body(...)
):
    async with aiohttp.ClientSession() as session:
        payload = {
            "main": {
                "platform": data.main.platform,
                "channel": data.main.channel,
                "author": {
                    "tag": data.main.author.tag,
                    "name": data.main.author.name
                },
                "message": {
                    "text": data.main.message.text,
                    "attachments": [
                        {"type": att.type, "data": att.data} for att in data.main.message.attachments
                    ]
                }
            },
            "created_at": data.created_at.isoformat(),
            "resend_at": data.resend_at.isoformat() if data.resend_at else None
        }
        try:
            async with session.post(TARGET_API_URL3, json=payload) as response:
                text = await response.text()
                print(f"Status: {response.status}")
                print(f"Response text: {text}")
                if response.status == 200:
                    result = await response.json()
                    return {"status": "sent", "response": result}
                else:
                    return {"status": "error", "response": text}
        except Exception as e:
            print(f"❌ Exception occurred while sending: {e}")
            return {"status": "exception", "error": str(e)}
