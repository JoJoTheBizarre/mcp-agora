from __future__ import annotations

import uuid
from collections import deque
from datetime import datetime, timezone
from typing import Optional

from .exceptions import AgentNotFoundError, BufferFullError, InvalidTokenError
from .models import (
    AgentCard,
    AgentIdentity,
    BufferConfig,
    Message,
    MessageType,
    MessageView,
)
from .names import generate_unique_name


class MessageBuffer:
    def __init__(self, config: Optional[BufferConfig] = None) -> None:
        self._config = config or BufferConfig()

        # fun_name → AgentIdentity
        self._agents: dict[str, AgentIdentity] = {}

        # token → fun_name  (private lookup table, never exposed)
        self._tokens: dict[str, str] = {}

        # Capped message log
        self._messages: deque[Message] = deque(maxlen=self._config.max_messages)

    def subscribe(self, card: AgentCard) -> AgentIdentity:
        """Register a new agent from its AgentCard.

        Returns an AgentIdentity containing:
          - fun_name  → public display name used in all messages
          - token     → private secret; the agent must present this on every
                        subsequent publish / unsubscribe call
        """
        if (
            self._config.max_agents is not None
            and len(self._agents) >= self._config.max_agents
        ):
            raise BufferFullError(self._config.max_agents)

        taken = set(self._agents.keys())
        fun_name = generate_unique_name(taken)
        token = str(uuid.uuid4())

        identity = AgentIdentity(
            fun_name=fun_name,
            token=token,
        )

        self._agents[fun_name] = identity
        self._tokens[token] = fun_name

        self._emit_system(f"{fun_name} joined the channel. ({card.description})")

        return identity

    def unsubscribe(self, token: str) -> None:
        """Remove an agent from the buffer using its private token."""
        fun_name = self._resolve_token(token)
        self._agents[fun_name].is_active = False
        del self._agents[fun_name]
        del self._tokens[token]
        self._emit_system(f"{fun_name} left the channel.")

    def publish(self, token: str, content: str) -> Message:
        """Post a message. The token is resolved to the agent's fun_name
        internally — the name is stamped on the message automatically."""
        fun_name = self._resolve_token(token)

        message = Message(
            id=str(uuid.uuid4()),
            author_name=fun_name,
            content=content,
            type=MessageType.CHAT,
        )
        self._messages.append(message)
        return message

    def get_messages(
        self,
        since: Optional[datetime] = None,
        limit: int = 50,
    ) -> list[MessageView]:
        """Return up to *limit* messages as slim MessageView objects (author, content, timestamp).
        Optionally filtered to those after *since*.
        """
        msgs = list(self._messages)

        if since is not None:
            since_aware = since if since.tzinfo else since.replace(tzinfo=timezone.utc)
            msgs = [m for m in msgs if m.timestamp > since_aware]

        return [
            MessageView(
                author_name=m.author_name, content=m.content, timestamp=m.timestamp
            )
            for m in msgs[-limit:]
        ]

    def list_subscribers(self) -> list[AgentIdentity]:
        """Return all currently active agents.
        Note: AgentIdentity includes the token field. Strip it before
        broadcasting this list to other agents if needed.
        """
        return list(self._agents.values())

    def get_agent_by_name(self, fun_name: str) -> AgentIdentity:
        """Look up an agent by their public fun_name."""
        try:
            return self._agents[fun_name]
        except KeyError:
            raise AgentNotFoundError(fun_name)

    @property
    def config(self) -> BufferConfig:
        return self._config

    def _resolve_token(self, token: str) -> str:
        """Resolve a token to a fun_name, raising InvalidTokenError if unknown."""
        try:
            return self._tokens[token]
        except KeyError:
            raise InvalidTokenError()

    def _emit_system(self, content: str) -> None:
        msg = Message(
            id=str(uuid.uuid4()),
            author_name="system",
            content=content,
            type=MessageType.SYSTEM,
        )
        self._messages.append(msg)

    def clear(self) -> None:
        """Wipe all messages and subscribers. Useful for testing."""
        self._messages.clear()
        self._agents.clear()
        self._tokens.clear()
