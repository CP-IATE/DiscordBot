from pydantic import BaseModel
from typing import List, Literal

class Author(BaseModel):
    tag: str
    name: str

class Attachment(BaseModel):
    #type: #Literal["image", "video", "audio", "archive", "document", "code", "gif","jpg"]
    type: str
    data: str

class Message(BaseModel):
    text: str
    attachments: List[Attachment] = []

class RequestData(BaseModel):
    platform: Literal["telegram", "discord"]
    channel: str
    author: Author
    message: Message

class DELETE(BaseModel):
    message_id: int