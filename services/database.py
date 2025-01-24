import logging
from pymongo.database import Database
from util.typings import ConversationRecord, Message, Result
from typing import List

class DatabaseService:
    def __init__(self, database: Database):
        self.database = database

    def get_conversation_record(self, guild_id: str, user_id: str) -> Result[ConversationRecord]:
        try:
            collection = self.database.get_collection("conversation_records")

            result = collection.find_one({
                "guild_id": guild_id,
                "user_id": user_id
            })

            if result:
                logging.info(f"Conversation record found for guild {guild_id} and user {user_id}")
                return Result.success(ConversationRecord(**result))
            else:
                logging.warning(f"No conversation record found for guild {guild_id} and user {user_id}")
                return Result.failure("No conversation record found.")
        except Exception as e:
            logging.error(f"There was an error getting the conversation record: {e}")
            return Result.failure(f"There was an error getting the conversation record")

    def insert_conversation_record(self, conversation_record: ConversationRecord) -> Result[None]:
        try:
            self.database.get_collection("conversation_records").insert_one(conversation_record.model_dump())
            return Result.success(None)
        except Exception as e:
            return Result.failure(f"There was an error inserting the conversation record: {e}")
        
    def update_conversation_record(self, conversation_record: ConversationRecord, message: List[Message]) -> Result[None]:
        try:
            self.database.get_collection("conversation_records").update_one(
                { "_id": conversation_record.id },
                {"$push": { "messages": {"$each": [msg.model_dump() for msg in message]} }}
            )
            return Result.success(None)
        except Exception as e:
            return Result.failure(f"There was an error updating the conversation record: {e}")
