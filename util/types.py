from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class Message(BaseModel):
    role: str
    content: str 
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())

class ConversationRecord(BaseModel):
    id: str = Field(alias="_id")
    user_id: int
    guild_id: int
    channel_id: int
    messages: List[Message] = Field(default_factory=list)
    last_updated: Optional[float] = Field(default_factory=lambda: datetime.now().timestamp())

    class Config:
        allow_population_by_field_name = True