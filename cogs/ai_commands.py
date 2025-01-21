# cogs/ai_commands.py

import discord
from discord import app_commands
from discord.ext import commands
import time

from config import ADMIN_ROLE_ID, SPECIAL_ROLE_ID, CONTEXT_TIMEOUT
from services.ai_service import AIService
from services.channel_service import ChannelService


class AICommands(commands.Cog):
    def __init__(self, bot: commands.Bot, ai_service: AIService):
        self.bot = bot
        self.ai_service = ai_service

    # Command to create a private AI channel
    @app_commands.command(name="open", description="Open a private AI chat session.")
    async def open_ai_chat(self, interaction: discord.Interaction):
        # Check if user already has a channel
        
        channel = await ChannelService.get_user_ai_channel(
            interaction.guild,
            interaction.user
        )
        
        if channel:
            await interaction.response.send_message(
                f"You already have an AI channel: {channel.mention}",
                ephemeral=True
            )
            return
            
        # Create new channel if none exists
        try:
            channel = await ChannelService.create_private_channel(
                interaction.guild,
                interaction.user,
                SPECIAL_ROLE_ID
            )
            
            await interaction.response.send_message(
                f"Private AI channel created: {channel.mention}",
                ephemeral=True
            )
            
            await self.ai_service.start_conversation(str(channel.id))
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to create channels. Please contact a server administrator.",
                ephemeral=True
            )
        except discord.HTTPException as e:
            await interaction.response.send_message(
                f"Failed to create channel due to Discord API error.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                "An unexpected error occurred while creating your channel. Please try again later.",
                ephemeral=True
            )

    # Command to talk to the AI in the private channel
    @app_commands.command(name="ask", description="Ask the AI a question.")
    async def ask_ai(self, interaction: discord.Interaction, query: str):
        conversation_id = str(interaction.channel.id)
        
        try:
            ai_reply = await self.ai_service.process_query(conversation_id, query)
            await interaction.response.send_message(ai_reply)
        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while processing your request.",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(AICommands(bot))
