import logging
from datetime import datetime

from pymongo.database import Database
from util import get_logger, get_system_message
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
                record = ConversationRecord(**result)
                return Result.success(record)

            logger.warning(f"No conversation record found for user {user_id} in guild {guild_id}.")

            system_message = get_system_message().data
            conversation = ConversationRecord(
                guild_id=guild_id,
                user_id=user_id,
                messages=[system_message]
            )

            self.collection.insert_one(conversation.model_dump(by_alias=True))

            logger.info(f"Created conversation record for user {user_id} in guild {guild_id}.")
            return Result.success(conversation)
        except Exception as e:
            logger.error(f"There was an error getting the conversation record from MongoDB Collection: {e}")
            return Result.failure("There was an unexpected error in the system."
                                  " Try again later and report the error the admins.")

    def add_message(self, conversation_record: ConversationRecord, messages: List[Any]) -> Result[None]:
        try:
            self.collection.update_one(
                {"_id": conversation_record.id},
                {
                    "$push": {"messages": {"$each": messages}},
                    "$set": {"last_updated": datetime.utcnow().timestamp()}
                },
            )
            return Result.success(None)
        except Exception as e:
            logger.error(f"There was an error updating the conversation record {conversation_record.id}: {e}")
            return Result.failure(f"There was an error updating the conversation record")

    def reset_conversation_record(self, conversation_record: ConversationRecord) -> Result[None]:
        try:
            system_message = get_system_message().data
            self.collection.update_one(
                {"_id": conversation_record.id},
                {"$set": {"messages": [system_message], "last_updated": datetime.utcnow().timestamp()}}
            )
            return Result.success(None)
        except Exception as e:
            logger.error(f"There was an error updating the conversation {conversation_record.id}: {e}")
            return Result.failure(f"There was an error resetting the conversation record")
