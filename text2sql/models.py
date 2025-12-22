from pydantic import BaseModel, Field
from uuid import uuid4
from time import time


class ConversationHistoryItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    username: str
    user_prompt: str
    response: str
    conversation_group_id: str
    created_at: int = Field(default_factory=lambda: int(time()))


class ProjectItem(BaseModel):
    project_id: str = Field(default_factory=lambda: str(uuid4()))
    project_name: str = Field(default_factory=lambda: "New Project")
    created_at: int = Field(default_factory=lambda: int(time()))
    username: str


class GroupedConversationItem(BaseModel):
    conversation_group_id: str = Field(default_factory=lambda: str(uuid4()))
    conversation_group_name: str = Field(default_factory=lambda: "New Chat")
    created_at: int = Field(default_factory=lambda: int(time()))
    username: str
    project_id: str
