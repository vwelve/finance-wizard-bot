import discord
from discord import DiscordException, PermissionOverwrite
from util import db, ConversationRecord, Result
import logging

class ConversationService:
    @staticmethod
    async def get_user_conversation(
        guild: discord.Guild,
        user: discord.Member
    ) -> Result[ConversationRecord]:
        logging.info(f"Getting conversation record for user {user.id} in guild {guild.id}")

        try:
            record_dict = db.get_collection("conversation_records").find_one({"user_id": user.id, "guild_id": guild.id})
            if not record_dict:
                logging.warning(f"No conversation record found for user {user.id} in guild {guild.id}")
                return Result.failure("No conversation record found.")

            conversation_record = ConversationRecord(**record_dict)
            if not guild.get_channel(conversation_record.channel_id):
                logging.warning(f"Channel no longer exists: {conversation_record.channel_id}")
                return Result.failure("Could not find your conversation channel.")

            logging.debug(f"Conversation Record: {conversation_record}")
            return Result.success(conversation_record)
        except DiscordException as e:
            logging.error(f"There was a DiscordException getting the conversation record: {e}")
            return Result.failure(f"There was an error getting the conversation record.")
        except Exception as e:
            logging.error(f"There was an unexpected error getting the conversation record: {e}")
            return Result.failure(f"There was an unexpected error getting the conversation record.")


    @staticmethod
    async def create_conversation_channel(
        guild: discord.Guild,
        user: discord.Member,
    ) -> Result[ConversationRecord]:
        overwrites = {
            guild.default_role: PermissionOverwrite(view_channel=False),
            user: PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: PermissionOverwrite(view_channel=True, send_messages=True),
        }

        logging.info(f"Creating conversation channel for user {user.id} in guild {guild.id}")

        try:
            logging.debug(f"Permission Overwrites:\n {overwrites}")
            channel = await guild.create_text_channel(
                name=f"ai-chat-{user.name}",
                overwrites=overwrites
            )

            conversation_record = ConversationRecord(
                user_id=user.id,
                guild_id=guild.id,
                channel_id=channel.id,
                messages=[]
            )

            db.get_collection("conversation_records").insert_one(conversation_record.model_dump())

            return Result.success(conversation_record)
        except Exception:
            return Result.failure(f"There was an error creating the conversation channel.")

    @staticmethod
    async def reset_conversation(
        conversation_record: ConversationRecord
    ) -> Result[None]:
        logging.info(f"Resetting conversation for user {conversation_record.user_id} in guild {conversation_record.guild_id}")

        try:
            db.get_collection("conversation_records").update_one(
                {"_id": conversation_record.id},
                {"$set": {"messages": []}}
            )
        except Exception as e:
            logging.error(f"There was an error resetting the conversation: {e}")
            return Result.failure(f"There was an error resetting the conversation.")

        return Result.success()

        