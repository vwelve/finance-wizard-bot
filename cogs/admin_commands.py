# cogs/admin_commands.py

import discord
from discord import app_commands
from discord.ext import commands
from config import ADMIN_ROLE_ID, SPECIAL_ROLE_ID

def is_admin_or_special_role():
    # Custom check to see if user has admin permissions or special role
    def predicate(interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            return True
        role_ids = [role.id for role in interaction.user.roles]
        return (ADMIN_ROLE_ID in role_ids) or (SPECIAL_ROLE_ID in role_ids)
    return app_commands.check(predicate)

class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="reset_all_ai_conversations")
    @is_admin_or_special_role()
    async def reset_all_ai_conversations(self, interaction: discord.Interaction):
        """
        An admin/special command to reset or purge all conversation data.
        """
        # Your logic to reset/purge from the DB
        # CAREFUL: This might drop entire collection
        await interaction.response.send_message("All AI conversations have been reset.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCommands(bot))
