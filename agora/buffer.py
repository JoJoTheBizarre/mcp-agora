import uuid
from collections import deque
from datetime import datetime, timezone
from typing import Optional

from .exceptions import AgentNotFoundError, BufferFullError
from .models import (
    AgentCard,
    AgentInfo,
    BufferConfig,
    Message,
    MessageType,
    MessageView,
)
from .names import generate_unique_name


class MessageBuffer:
    def __init__(self, config: Optional[BufferConfig] = None) -> None:
        self._config = config or BufferConfig()
        self._agents: dict[str, AgentCard] = {}
        self._messages: deque[Message] = deque(maxlen=self._config.max_messages)

    def subscribe(self, card: AgentCard) -> str:
        """Register an agent. Returns its assigned fun_name."""
        if (
            self._config.max_agents is not None
            and len(self._agents) >= self._config.max_agents
        ):
            raise BufferFullError(self._config.max_agents)

        fun_name = generate_unique_name(taken=set(self._agents.keys()))
        self._agents[fun_name] = card
        self._emit_system(f"{fun_name} joined the channel.")
        return fun_name

    def unsubscribe(self, fun_name: str) -> None:
        """Remove an agent from the buffer."""
        self._get_agent(fun_name)
        del self._agents[fun_name]
        self._emit_system(f"{fun_name} left the channel.")

    def publish(self, fun_name: str, content: str) -> Message:
        """Post a message on behalf of fun_name."""
        self._get_agent(fun_name)
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
        """Return up to limit messages, optionally filtered to those after since."""
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

    def list_agents(self) -> list[AgentInfo]:
        """Return the name and description of every active agent."""
        return [
            AgentInfo(fun_name=name, description=card.description)
            for name, card in self._agents.items()
        ]

    def clear(self) -> None:
        """Wipe all messages and agents."""
        self._messages.clear()
        self._agents.clear()

    def _get_agent(self, fun_name: str) -> AgentCard:
        try:
            return self._agents[fun_name]
        except KeyError:
            raise AgentNotFoundError(fun_name)

    def _emit_system(self, content: str) -> None:
        self._messages.append(
            Message(
                id=str(uuid.uuid4()),
                author_name="system",
                content=content,
                type=MessageType.SYSTEM,
            )
        )
