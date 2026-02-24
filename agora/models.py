from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AgentCard(BaseModel):
    """Presented by an agent when it wants to join the buffer.
    The agent only describes its capabilities — the buffer handles naming.
    """

    description: str = Field(
        ..., description="What this agent does / its capabilities."
    )


class AgentIdentity(BaseModel):
    """Returned to the agent after a successful subscription.

    - fun_name is the public display name shown in all messages.
    - token is the private secret the agent must present on every publish call.
      It is returned once on subscribe and never broadcast again.
    """

    fun_name: str = Field(
        ..., description="Unique, human-readable display name (e.g. 'Orion')."
    )
    token: str = Field(
        ..., description="Private UUID4 token. Must be presented on every publish call."
    )
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True


class MessageType(str, Enum):
    CHAT = "chat"
    SYSTEM = "system"  # join / leave events


class Message(BaseModel):
    id: str = Field(..., description="Unique message ID (UUID4).")
    author_name: str = Field(..., description="fun_name of the sender, or 'system'.")
    content: str
    type: MessageType = MessageType.CHAT
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MessageView(BaseModel):
    """Slim read-only projection returned by get_messages.
    Contains only what agents need to see — no internal IDs or type metadata.
    """

    author_name: str
    content: str
    timestamp: datetime


class BufferConfig(BaseModel):
    max_messages: int = Field(
        default=500,
        ge=1,
        description="Max messages held in memory before oldest are evicted.",
    )
    max_agents: Optional[int] = Field(
        default=None, description="Cap on concurrent subscribers. None = unlimited."
    )
