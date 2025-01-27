from .typings import ConversationRecord, Result
from .logging import setup_logging, get_logger
from .mongo_client import db

logger = get_logger(__name__)

file = open("system-message.txt", "r")
system_message = file.read()


def get_system_message():
    logger.debug(f"Retrieving system message {system_message}")
    return Result.success({
        "role": "system",
        "content": system_message
    })
