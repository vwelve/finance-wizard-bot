import json
import os
from datetime import datetime
from typing import Tuple, Any, List, Dict

from openai import OpenAI
from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageToolCall

from config import XAI_API_KEY
from services.database import DatabaseService

from util import ConversationRecord, get_logger
from util.search_web import search_web
from util.typings import Result

logger = get_logger(__name__)

MODEL = "grok-2-1212"
MAX_TOTAL_TOKENS = 131072
AVAILABLE_FUNCTIONS = {
    "search_web": search_web
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "If a user requests data on a stock I don't have, I'll search a link like ["
                           "https://finance.yahoo.com/quote/TICKER/history?p=TICKER] or from trading view like ["
                           "https://www.tradingview.com/symbols/SYMBOL]. Also use if you need real time data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The URL or information you want to with the format of ["
                                       "https://finance.yahoo.com/quote/TICKER/history?p=TICKER] or "
                                       "[https://www.tradingview.com/symbols/SYMBOL]",
                    },
                },
                "required": ["prompt"],
            },
        },
    }
]


async def handle_tools(tool_calls: List[ChatCompletionMessageToolCall]) -> Result[List[Any]]:
    try:
        tool_responses = []

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = AVAILABLE_FUNCTIONS.get(function_name)
            function_args = json.loads(tool_call.function.arguments)

            function_response = await function_to_call(prompt=function_args.get("prompt"))

            tool_responses.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response
                }
            )

        return Result.success(tool_responses)
    except Exception as e:
        logger.critical(f"Error calling tools {e}")
        return Result.failure("Could not retrieve real time data from the internet. "
                              "Try again later or report to administrators")


class AIService:
    def __init__(self, db: DatabaseService):
        self.db = db
        logger.info(f"XAI_API_KEY: {XAI_API_KEY}")
        self.client = OpenAI(
            api_key=XAI_API_KEY,
            base_url="https://api.x.ai/v1"
        )

    @staticmethod
    def create_user_message(msg: str) -> Result[Dict[str, Any]]:
        logger.debug(f"Create user message with {msg}")
        return Result.success({
            "role": "user",
            "content": msg
        })

    async def _send_message(
            self,
            conversation: ConversationRecord,
            messages: List[Dict[str, Any]]
    ) -> Result[Tuple[ChatCompletionMessage, int]]:
        try:

            completion = self.client.chat.completions.create(
                model=MODEL,
                messages=[*conversation.messages, *messages],
                tools=TOOLS
            )

            response_message = completion.choices[0].message
            total_tokens = completion.usage.total_tokens

            if not response_message.tool_calls:
                self.db.add_message(conversation, [*messages, response_message.model_dump()])

                return Result.success((response_message, total_tokens))

            result = await handle_tools(response_message.tool_calls)

            if not result.success:
                return Result.failure(result.error)

            tool_responses = result.data
            return await self._send_message(conversation, [*messages, response_message.model_dump(), *tool_responses])
        except Exception as e:
            logger.critical(f"Errors trying to send a message to Grok AI {e}")
            return Result.failure("Could not reach Grok AI. Report this error to the administrators")

    async def send_message(
            self,
            conversation: ConversationRecord,
            content: str
    ) -> Result[Tuple[ChatCompletionMessage, int]]:
        if datetime.utcnow().timestamp() - conversation.last_updated >= 86400:
            self.db.reset_conversation_record(conversation)

        message = self.create_user_message(content).data
        result = await self._send_message(conversation, [message])
        return result


