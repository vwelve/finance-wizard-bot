# cogs/ai_commands.py

import discord
from discord import app_commands
from discord.ext import commands

from services import ConversationService
from services.ai_service import AIService
from services.database import DatabaseService
from util import db


class AICommands(commands.Cog):
    def __init__(self, bot: commands.Bot, ai: AIService, conversation_service: ConversationService):
        self.bot = bot
        self.ai = ai
        self.conversation_service = conversation_service

    # Command to create a private AI channel
    @app_commands.command(name="open", description="Open a private AI chat session.")
    async def open_ai_chat(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        guild = interaction.guild
        user = interaction.user

        result = await self.conversation_service.get_user_conversation(guild, user)

        if result.success:
            await interaction.followup.send(f"You can send messages in <#{result.data.channel_id}>")
            return

        result = await self.conversation_service.create_conversation_channel(guild, user)
        text_channel = result.data

        if result.success:
            # Create a private AI channel
            await interaction.followup.send(f"Opening AI chat session in <#{text_channel.id}>")
        else:
            await interaction.followup.send(result.error)

    # Command to talk to the AI in the private channel
    @app_commands.command(name="ask", description="Ask the AI a question.")
    async def ask_ai(self, interaction: discord.Interaction):
        await interaction.response.send_message("Asking AI a question...")

    async def cog_load(self):
        pass
        

async def setup(bot: commands.Bot):
    db_service = DatabaseService(db)
    ai_service = AIService(db_service)
    conversation_service = ConversationService(db_service)

    await bot.add_cog(AICommands(bot, ai_service, conversation_service))
