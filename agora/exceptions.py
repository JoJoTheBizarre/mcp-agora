class AgoraError(Exception):
    """Base exception for all Agora errors."""


class AgentNotFoundError(AgoraError):
    def __init__(self, fun_name: str):
        super().__init__(f"No active agent with name '{fun_name}'.")
        self.fun_name = fun_name


class AgentAlreadySubscribedError(AgoraError):
    def __init__(self, fun_name: str):
        super().__init__(f"Agent '{fun_name}' is already subscribed.")
        self.fun_name = fun_name


class BufferFullError(AgoraError):
    def __init__(self, max_agents: int):
        super().__init__(f"Buffer is at capacity ({max_agents} agents).")
        self.max_agents = max_agents
