from typing import Optional

import discord
from discord import DiscordException, PermissionOverwrite, Forbidden, TextChannel
from services.database import DatabaseService
from util import ConversationRecord, get_logger
from util.typings import Result
import logging

logger = get_logger(__name__)


class ConversationService:
    def __init__(self, db: DatabaseService):
        self.db = db

    async def get_user_conversation(
            self,
            guild: discord.Guild,
            user: discord.Member
    ) -> Result[ConversationRecord]:
        logger.info(f"Getting conversation record for user {user.id} in guild {guild.id}")

        try:
            result = self.db.get_conversation_record(guild.id, user.id)
            if not result.success:
                logger.warning(f"No conversation record found for user {user.id} in guild {guild.id}")
                return Result.failure("No conversation record found.")

            conversation_record = ConversationRecord(**result.data)
            if not guild.get_channel(conversation_record.channel_id):
                logger.warning(f"Channel no longer exists: {conversation_record.channel_id}")
                return Result.failure("Could not find your conversation channel.")

            logger.debug(f"Conversation Record: {conversation_record}")
            return Result.success(conversation_record)
        except DiscordException as e:
            logger.error(f"There was a DiscordException getting the conversation record: {e}")
            return Result.failure(f"There was an error getting the conversation record.")
        except Exception as e:
            logger.error(f"There was an unexpected error getting the conversation record: {e}")
            return Result.failure(f"There was an unexpected error getting the conversation record.")

    async def create_conversation_channel(
            self,
            guild: discord.Guild,
            user: discord.Member,
    ) -> Result[Optional[TextChannel]]:
        overwrites = {
            guild.default_role: PermissionOverwrite(view_channel=False),
            user: PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: PermissionOverwrite(view_channel=True, send_messages=True),
        }

        logger.info(f"Creating conversation channel for user {user.id} in guild {guild.id}")

        try:
            logger.debug(f"Permission Overwrites:\n {overwrites}")
            channel = await guild.create_text_channel(
                name=f"ai-chat-{user.name}",
                overwrites=overwrites
            )

            result = self.db.create_conversation_record(guild.id, user.id, channel.id)

            if not result.success:
                return result

            return Result.success(channel)
        except Forbidden as e:
            logger.error(f"Permissions error when trying to create a channel for {user.id} in {guild.id}: {e}")
            return Result.failure(f"I do not have the permissions to create a channel for you. Tell the administrators "
                                  f"about this error.")
        except Exception as e:
            logger.error(f"Received unexpected error: {e}")
            return Result.failure(f"There was an error creating the conversation channel.")
