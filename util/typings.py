from typing import Any, List, Generic, TypeVar, Optional

from bson import ObjectId
from pydantic import BaseModel, Field
from datetime import datetime

# Define a generic type variable
T = TypeVar("T")


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if not ObjectId.is_valid(value):
            raise ValueError(f"Invalid ObjectId: {value}")
        return ObjectId(value)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class ConversationRecord(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: int
    guild_id: int
    channel_id: int
    messages: List[Any] = Field(default_factory=list)
    last_updated: Optional[float] = Field(default_factory=lambda: datetime.now().timestamp())

    class Config:
        allow_population_by_field_name = True


class Result(Generic[T]):
    def __init__(self, success: bool, data: Optional[T] = None, error: Optional[str] = None):
        self.success = success
        self.data = data  # The type of data is now generic
        self.error = error  # Error message (string)

    @staticmethod
    def success(data: T = None) -> "Result[T]":
        return Result(True, data=data)

    @staticmethod
    def failure(error: str) -> "Result[T]":
        return Result(False, error=error)

    def __repr__(self):
        if self.success:
            return f"Result(success=True, data={self.data})"
        else:
            return f"Result(success=False, error='{self.error}')"
