# cogs/ai_commands.py
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from config import SECRET_CHANNEL_ID, SPECIAL_ROLE_ID
from services.ai_service import AIService
from services.database import DatabaseService
from util import db, get_logger

logger = get_logger(__name__)

class AICommands(commands.Cog):
    def __init__(self, bot: commands.Bot, db_service: DatabaseService, ai: AIService):
        self.bot = bot
        self.ai = ai
        self.db = db_service

    # Command to talk to the AI in the private channel
    @app_commands.command(name="ask", description="Ask the AI a question.")
    async def ask_ai(self, interaction: discord.Interaction, *, content: str):
        await interaction.response.defer(thinking=True)

        guild = interaction.guild
        user = interaction.user

        logger.info(f"Checking {SECRET_CHANNEL_ID} is eq to {interaction.channel_id}")
        if SECRET_CHANNEL_ID != interaction.channel_id:
            await interaction.followup.send(f"You can only use this command in <#{SECRET_CHANNEL_ID}>")
            return

        logger.info(f"Checking if user {user.id} has role: {SPECIAL_ROLE_ID}")
        if SPECIAL_ROLE_ID not in [role.id for role in user.roles]:
            await interaction.followup.send(f"You don't have the required role to use this command.")
            return

        result = self.db.get_conversation_record(guild.id, user.id)

        if not result.success:
            await interaction.followup.send(result.error)

        conversation = result.data
        result = await self.ai.send_message(conversation, content)

        if result.success:
            data = result.data
            chat_response = data[0]
            await interaction.followup.send(chat_response.content)
        else:
            await interaction.followup.send(result.error)

    async def cog_load(self):
        pass
        

async def setup(bot: commands.Bot):
    db_service = DatabaseService(db)
    ai_service = AIService(db_service)

    await bot.add_cog(AICommands(bot, db_service, ai_service))
