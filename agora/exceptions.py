class AgoraError(Exception):
    """Base exception for all Agora errors."""


class AgentNotFoundError(AgoraError):
    """Raised when an operation references a fun_name that isn't subscribed."""

    def __init__(self, fun_name: str):
        super().__init__(f"No active agent with name '{fun_name}'.")
        self.fun_name = fun_name


class InvalidTokenError(AgoraError):
    """Raised when a publish or unsubscribe call presents an unrecognised token."""

    def __init__(self):
        super().__init__("Invalid or expired token.")


class AgentAlreadySubscribedError(AgoraError):
    """Raised when the same proposed_name tries to subscribe twice while still active."""

    def __init__(self, proposed_name: str):
        super().__init__(f"Agent '{proposed_name}' is already subscribed.")
        self.proposed_name = proposed_name


class BufferFullError(AgoraError):
    """Raised when max_agents cap has been reached."""

    def __init__(self, max_agents: int):
        super().__init__(f"Buffer is at capacity ({max_agents} agents).")
        self.max_agents = max_agents
