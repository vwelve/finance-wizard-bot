import discord
from discord.ext import commands
import asyncio
import os
import logging
from config import DISCORD_BOT_TOKEN
from util.logging import setup_logging


logger = logging.getLogger(__name__)

# In discord.py 2.0, we can use commands.Bot with intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

setup_logging()

bot = commands.Bot(command_prefix="!", intents=intents)

# Load cogs
initial_extensions = [
    "cogs.admin_commands",
    "cogs.ai_commands"
]

@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")

    # Sync application commands with Discord
    # Make sure your bot has the applications.commands scope in the Developer Portal
    try:
        GUILD_ID = 840650643839778867
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)

        for guild in bot.guilds:
            await bot.tree.sync(guild=guild)

        logger.info(f"Commands synced to guild {GUILD_ID}!")
    except Exception as e:
        logger.error(f"Failed to sync commands: {str(e)}")


async def main():
    for ext in initial_extensions:
        await bot.load_extension(ext)
    await bot.start(DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
