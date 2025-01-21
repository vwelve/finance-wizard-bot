from typing import List, Dict, Any
from services.openai_service import get_ai_response
from database.conversation_service import ConversationService
import time

class AIService:
    def __init__(self, conversation_service: ConversationService):
        self.conversation_service = conversation_service

    async def start_conversation(self, conversation_id: str) -> None:
        self.conversation_service.save_message(conversation_id, {
            "role": "system",
            "content": "Conversation started.",
            "timestamp": time.time()
        })

    async def process_query(self, conversation_id: str, query: str) -> str:
        # Save user message
        user_message = {
            "role": "user",
            "content": query,
            "timestamp": time.time()
        }
        self.conversation_service.save_message(conversation_id, user_message)
        
        # Get conversation history
        conversation = self.conversation_service.get_conversation(conversation_id)
        messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in conversation.get("messages", [])
        ]
        
        # Get AI response
        ai_reply = get_ai_response(messages)
        
        # Save AI response
        self.conversation_service.save_message(conversation_id, {
            "role": "assistant",
            "content": ai_reply,
            "timestamp": time.time()
        })
        
        return ai_reply 