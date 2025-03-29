from utils import encode_file_to_base64

def setup_event_handlers (client):
    @client.event
    async def on_ready():
        print(f"Bot {client.user} is running...!")

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if message.content.strip():
            print(f"[{message.guild.name} | {message.channel.name}] {message.author}: {message.content}")

            """request_data = RequestData(
                platform="discord",
                author=Author(tag=message.author.name, name=message.author.display_name),
                message=Message(
                    text=message.content,
                    attachments=[]
                )
            )
            #request_data = DELETE(text = message.content)
            await telegram(request_data)"""

        for attachment in message.attachments:
            print(f"📂 Отримано файл: {attachment.filename} ({attachment.size} байт)\n")
            file_bytes = await attachment.read()
            base64_data = encode_file_to_base64(file_bytes)

            """files = []
            image_bytes = base64.b64decode(base64_data)
            file = discord.File(io.BytesIO(image_bytes), filename="image.png")  # filename=attachment.filename
            files.append(file)
            channel = client.get_channel(message.channel.id)
            await channel.send(files=files if files else None)"""

            """request_data = RequestData(
                platform="discord",
                author=Author(tag=message.author.name, name=message.author.display_name),
                message=Message(
                    text=message.content,
                    attachments= [Attachment(type = "image", data=base64_data)]
                )
            )
            await send_message_to_telegram()(request_data)"""
            print(f"📂 Файл: {attachment.filename} закодовано в Base64! - {base64_data}")

            # if message.content.strip():
            #    file_bytes = await attachment.read()