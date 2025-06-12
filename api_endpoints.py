from bot import client
import discord
from models import RequestData, DELETE
from utils import decode_base64_to_file
from fastapi import Body, APIRouter

router = APIRouter()

@router.post("/discord-telegram/")
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


@router.delete("/discord-telegram/")
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