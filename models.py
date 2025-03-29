from pydantic import BaseModel
from typing import List, Literal

class Author(BaseModel):
    tag: str
    name: str

class Attachment(BaseModel):
    type: Literal["image", "archive", "gif"]  # Додати інші типи
    data: str           #List[int]

class Message(BaseModel):
    text: str
    attachments: List[Attachment] = [] # Не обов'язково

class RequestData(BaseModel):
    platform: Literal["telegram", "discord"]
    author: Author
    message: Message

class DELETE(BaseModel):
    message_id: int