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
