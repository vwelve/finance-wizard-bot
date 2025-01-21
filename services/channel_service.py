from typing import Dict
import discord
from discord import PermissionOverwrite

class ChannelService:
    @staticmethod
    async def get_user_ai_channel(
        guild: discord.Guild,
        user: discord.Member
    ) -> discord.TextChannel:
        

        return await guild.create_text_channel(
            name=f"ai-chat-{user.name}",
            overwrites={
                guild.default_role: PermissionOverwrite(view_channel=False),
                user: PermissionOverwrite(view_channel=True, send_messages=True),
                guild.me: PermissionOverwrite(view_channel=True, send_messages=True),
            }
        )


    @staticmethod
    async def create_private_channel(
        guild: discord.Guild,
        user: discord.Member,
        special_role_id: int
    ) -> discord.TextChannel:
        overwrites = {
            guild.default_role: PermissionOverwrite(view_channel=False),
            user: PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: PermissionOverwrite(view_channel=True, send_messages=True),
        }

        if special_role := guild.get_role(special_role_id):
            overwrites[special_role] = PermissionOverwrite(view_channel=True)

        return await guild.create_text_channel(
            name=f"ai-chat-{user.name}",
            overwrites=overwrites
        ) 