from pydantic import BaseModel, Field
from uuid import uuid4
from time import time


class ConversationHistoryItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    username: str
    user_prompt: str
    response: str
    username: str
    created_at: int = Field(default_factory=lambda: int(time()))


class GroupedConversationItem(BaseModel):
    conversation_grouped_id: str = Field(default_factory=lambda: str(uuid4()))
    conversation_grouped_name: str = Field(default_factory=lambda: "New Chat")
    created_at: int = Field(default_factory=lambda: int(time()))
    username: str
