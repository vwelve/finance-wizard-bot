import json
import os
from typing import Tuple, Any, List, Mapping

from openai import OpenAI
from openai.types.chat import ChatCompletionMessage

from services.database import DatabaseService
from services.openai_service import get_ai_response
import time

from util import ConversationRecord, get_logger
from util.search_web import search_web
from util.typings import Result

logger = get_logger(__name__)

MODEL = "grok-2-1212"
MAX_TOTAL_TOKENS = 131072
AVAILABLE_FUNCTIONS = {
    "search_web": search_web
}

file = open("system-message.txt", "r")
system_message = file.read()


async def handle_tools(tool_calls: Any) -> Result[List[Any]]:
    try:
        tool_responses = []

        for tool_call in tool_calls:
            function_name = tool_call["function"]["name"]
            function_to_call = AVAILABLE_FUNCTIONS.get(function_name)
            function_args = json.loads(tool_call["function"]["arguments"])

            function_response = await function_to_call(prompt=function_args.get("prompt"))

            tool_responses.append(
                {
                    "tool_call_id": tool_call["id"],
                    "role": "tool",
                    "name": function_name,
                    "content": function_response
                }
            )

        return Result.success(tool_responses)
    except Exception as e:
        logging.error(f"Unexpected error calling tools {e}")
        return Result.failure("Received an unexpected error trying to call to the web")


class AIService:
    def __init__(self, db: DatabaseService):
        self.db = db
        self.client = OpenAI(
            api_key=os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1"
        )

    @staticmethod
    def get_system_message():
        logging.debug(f"Retrieving system message {system_message}")
        return Result.success({
            "role": "system",
            "content": system_message
        })

    @staticmethod
    def create_user_message(msg: str) -> Result[Mapping[str, Any]]:
        logging.debug(f"Create user message with {msg}")
        return Result.success({
            "role": "user",
            "content": msg
        })

    async def send_message(
            self,
            conversation: ConversationRecord,
            messages: List[Mapping[str, Any]]
    ) -> Result[Tuple[ChatCompletionMessage, int]]:
        try:
            completion = self.client.chat.completions.create(
                model=MODEL,
                messages=[*conversation, *messages]
            )

            response_message = completion.choices[0].message
            total_tokens = completion.usage.total_tokens

            if response_message.tool_calls:
                tool_responses = handle_tools(response_message.tool_calls)
                return self.send_message(self, conversation, [*messages, response_message, *tool_responses])

            self.db.update_conversation_record(conversation, [*messages, response_message])

            return Result.success((response_message, total_tokens))
        except Exception as e:
            logging.error(f"Unexpected errors trying to send a message {e}")
            return Result.failure("Unexpected errors trying to send message.")
