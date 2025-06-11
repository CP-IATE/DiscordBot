import discord
from discord.ext import commands
from pymongo import MongoClient
from datetime import datetime
import asyncio
from dbContext import add_post
import re
from models import Post, RequestData, Author, Message, Attachment
from utils import encode_file_to_base64, decode_base64_to_file

# Dictionary to store user states
user_states = {}

class PostState:
    def __init__(self):
        self.content = None
        self.files = []
        self.channel_id = None
        self.resend_at = None
        self.step = "waiting_for_content"

async def process_dm_message(message):
    if message.content != "!post":
        return

    # Initialize state for user
    user_states[message.author.id] = PostState()
    await message.channel.send("Будь ласка, надішліть текст публікації та/або файли. Коли закінчите, напишіть 'done'.")

async def handle_post_content(message):
    if message.author.id not in user_states:
        return

    state = user_states[message.author.id]
    
    if state.step == "waiting_for_content":
        if message.content.lower() == "done":
            if not state.content and not state.files:
                await message.channel.send("Публікація не може бути порожньою. Будь ласка, додайте текст або файли.")
                return
            
            state.step = "channel"
            await message.channel.send("Введіть ID:")
        else:
            if message.content:
                state.content = message.content
            if message.attachments:
                state.files.extend(message.attachments)

    elif state.step == "channel":
        if message.content:
            state.channel_id = message.content
            state.step = "asking_resend"
            await message.channel.send("Чи потрібно запланувати повторне надсилання? (так/ні)")

    elif state.step == "asking_resend":
        if message.content.lower() in ["так", "yes", "y"]:
            state.step = "waiting_for_date"
            await message.channel.send("Введіть дату та час у форматі DD.MM.YYYY HH:MM")
        elif message.content.lower() in ["ні", "no", "n"]:
            await save_post_to_db(message)
        else:
            await message.channel.send("Будь ласка, відповідь 'так' або 'ні'")
    
    elif state.step == "waiting_for_date":
        try:
            date_str = message.content.strip()
            resend_date = datetime.strptime(date_str, "%d.%m.%Y %H:%M")
            print(resend_date)
            if resend_date < datetime.now():
                await message.channel.send("Дата не може бути в минулому. Спробуйте ще раз.")
                return
            state.resend_at = resend_date
            await save_post_to_db(message)
        except ValueError:
            await message.channel.send("Неправильний формат дати. Використовуйте формат DD.MM.YYYY HH:MM")

async def save_post_to_db(message):
    state = user_states[message.author.id]
    
    # Prepare attachments
    attachments = []
    for file in state.files:
        file_bytes = await file.read()
        base64_data = encode_file_to_base64(file_bytes)
        attachments.append(Attachment(
            type=file.content_type or "document",
            data=base64_data
        ))

    # Create RequestData
    request_data = RequestData(
        platform="discord",
        channel=str(state.channel_id),
        author=Author(
            tag=str(message.author.id),
            name=message.author.display_name
        ),
        message=Message(
            text=state.content or "",
            attachments=attachments
        )
    )

    # Create Post
    post = Post(
        main=request_data,
        created_at=datetime.utcnow(),
        resend_at=state.resend_at
    )

    # Save to MongoDB
    add_post(post)
    
    # Send confirmation
    await message.channel.send("✅ Публікацію успішно збережено!")

    # Clean up state
    del user_states[message.author.id]