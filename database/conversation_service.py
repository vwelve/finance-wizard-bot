from typing import Dict, Optional
import time
from util.mongo_client import MongoClient

class ConversationService:
    def __init__(self, mongo_client: MongoClient):
        self.mongo_client = mongo_client
        self.collection = self.mongo_client.get_conversation_collection()

    def save_message(self, conversation_id: str, message_data: Dict) -> None:
        self.collection.update_one(
            {"_id": conversation_id},
            {"$push": {"messages": message_data}},
            upsert=True
        )
        self.update_timestamp(conversation_id)

    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        return self.collection.find_one({"_id": conversation_id})

    def reset_conversation(self, conversation_id: str) -> None:
        self.collection.update_one(
            {"_id": conversation_id},
            {"$set": {"messages": []}}
        )

    def update_timestamp(self, conversation_id: str) -> None:
        self.collection.update_one(
            {"_id": conversation_id},
            {"$set": {"last_updated": time.time()}}
        ) 