# database/mongo_client.py

import pymongo
from pymongo import MongoClient
from config import MONGODB_URI

# Create a single, global MongoDB client so we don't recreate it multiple times
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client["discord_bot_database"]  # Use your preferred DB name

def get_conversation_collection():
    return db["conversations"]

def save_message(conversation_id: str, message_data: dict):
    coll = get_conversation_collection()
    coll.update_one(
        {"_id": conversation_id},
        {"$push": {"messages": message_data}},
        upsert=True
    )

def create_conversation(channel_id: int, user_id: int, guild_id: int):
    pass

def get_conversation(conversation_id: str):
    coll = get_conversation_collection()
    return coll.find_one({"_id": conversation_id})

def reset_conversation(conversation_id: str):
    coll = get_conversation_collection()
    coll.update_one(
        {"_id": conversation_id},
        {"$set": {"messages": []}}
    )

def update_timestamp(conversation_id: str, timestamp: float):
    coll = get_conversation_collection()
    coll.update_one(
        {"_id": conversation_id},
        {"$set": {"last_updated": timestamp}}
    )
# Add more helper methods as needed, e.g., for fetching timeouts, etc.
