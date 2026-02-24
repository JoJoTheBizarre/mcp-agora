from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AgentCard(BaseModel):
    """Presented by an agent on subscribe. Just a capability description."""

    description: str


class AgentInfo(BaseModel):
    """Public view of an active agent — name and description only."""

    fun_name: str
    description: str


class MessageType(str, Enum):
    CHAT = "chat"
    SYSTEM = "system"


class Message(BaseModel):
    """Full internal message record."""

    id: str
    author_name: str
    content: str
    type: MessageType = MessageType.CHAT
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MessageView(BaseModel):
    """Slim read-only projection returned by get_messages."""

    author_name: str
    content: str
    timestamp: datetime


class BufferConfig(BaseModel):
    max_messages: int = Field(default=500, ge=1)
    max_agents: Optional[int] = Field(default=None)
