import logging
from pymongo.database import Database

from services.ai_service import AIService
from util import get_logger
from util.typings import ConversationRecord, Result
from typing import List, Any

logger = get_logger(__name__)


class DatabaseService:
    def __init__(self, database: Database):
        self.collection = database.get_collection("conversation_records")

    def get_conversation_record(self, guild_id: int, user_id: int) -> Result[ConversationRecord]:
        try:
            result = self.collection.find_one({
                "guild_id": guild_id,
                "user_id": user_id
            })

            if result:
                logger.info(f"Conversation record found for guild {guild_id} and user {user_id}")
                return Result.success(ConversationRecord(**result))
            else:
                logger.warning(f"No conversation record found for guild {guild_id} and user {user_id}")
                return Result.failure("No conversation record found.")
        except Exception as e:
            logger.error(f"There was an error getting the conversation record: {e}")
            return Result.failure(f"There was an error getting the conversation record")

    def create_conversation_record(self, guild_id: int, user_id: int, channel_id: int) -> Result[None]:
        try:
            system_message = AIService.get_system_message().data
            conversation_record = ConversationRecord(
                guild_id=guild_id,
                user_id=user_id,
                channel_id=channel_id,
                messages=[system_message]
            )
            self.collection.insert_one(conversation_record.model_dump())
            return Result.success(None)
        except Exception as e:
            logger.error(f"There was an error inserting the conversation record: {e}")
            return Result.failure(f"There was an error inserting the conversation record")

    def update_conversation_record(self, conversation_record: ConversationRecord, message: List[Any]) -> Result[None]:
        try:
            self.collection.update_one(
                {"_id": conversation_record.id},
                {"$push": {"messages": {"$each": [msg.model_dump() for msg in message]}}}
            )
            return Result.success(None)
        except Exception as e:
            logger.error(f"There was an error updating the conversation record {conversation_record.id}: {e}")
            return Result.failure(f"There was an error updating the conversation record")

    def reset_conversation_record(self, conversation_record: ConversationRecord) -> Result[None]:
        try:
            self.collection.update_one(
                {"_id": conversation_record.id},
                {"$set": {"messages": []}}
            )
            return Result.success(None)
        except Exception as e:
            logger.error(f"There was an error updating the conversation {conversation_record.id}: {e}")
            return Result.failure(f"There was an error resetting the conversation record")
