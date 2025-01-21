# main.py

import discord
from discord.ext import commands
import asyncio
import os

from config import DISCORD_BOT_TOKEN
from util.logging import setup_logging

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
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

    # Sync application commands with Discord
    # Make sure your bot has the applications.commands scope in the Developer Portal
    try:
        for guild in bot.guilds:
            await bot.tree.sync(guild=guild)
        print("Commands synced successfully.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

async def main():
    for ext in initial_extensions:
        await bot.load_extension(ext)
    await bot.start(DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
