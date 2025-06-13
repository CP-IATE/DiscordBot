from pymongo import MongoClient
from typing import Optional, Dict, Any
from models import User, Post, RequestData
from config import MONGODB_HOST, MONGODB_PORT, MONGODB_DB_NAME
from datetime import datetime


client = MongoClient(MONGODB_HOST, int(MONGODB_PORT))
db = client[MONGODB_DB_NAME]
users_collection = db["users"]
post_collection = db["posts"]

def add_user(user: User) -> None:
    users_collection.insert_one(user.model_dump(exclude_none=True))

def add_post(post: Post) -> None:
    post_collection.insert_one(post.model_dump(exclude_none=True))

def check_user_is_admin(discord_id: int) -> Optional[Dict[str, Any]]:
    return users_collection.find_one({"discord_id": discord_id, "role": "admin"})

