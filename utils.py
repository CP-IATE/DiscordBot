import base64
import io
import discord

def encode_file_to_base64(file_bytes: bytes) -> str:
    """Code into Base64"""
    return base64.b64encode(file_bytes).decode("utf-8")

def decode_base64_to_file(base64_data: str, filename) -> discord.File:
    """Decode Base64 to file for Discord"""
    file_bytes = base64.b64decode(base64_data)
    return discord.File(io.BytesIO(file_bytes), filename=filename)
