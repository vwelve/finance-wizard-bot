# config.py

import os
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Required environment variables
required_env_vars = {
    "DISCORD_BOT_TOKEN": os.getenv("DISCORD_BOT_TOKEN"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "MONGODB_URI": os.getenv("MONGODB_URI"),
    "SPECIAL_ROLE_ID": os.getenv("SPECIAL_ROLE_ID")
}

# Check for missing environment variables
missing_vars = [var for var, value in required_env_vars.items() if not value]

if missing_vars:
    error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
    logger.critical(error_msg)
    raise EnvironmentError(error_msg)

# Assign the validated environment variables
DISCORD_BOT_TOKEN = required_env_vars["DISCORD_BOT_TOKEN"]
OPENAI_API_KEY = required_env_vars["OPENAI_API_KEY"]
MONGODB_URI = required_env_vars["MONGODB_URI"]
SPECIAL_ROLE_ID = required_env_vars["SPECIAL_ROLE_ID"]

# Time / Tokens Settings
MAX_TOKENS = 131072      # Example token limit
CONTEXT_TIMEOUT = 86400 # 24 hours in seconds
