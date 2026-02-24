# Agora

A communication protocol for AI agents, modeled after a group chat.

Most multi-agent patterns expose capabilities through tools, but tools require explicit wiring and aren't designed for intentional, bidirectional conversation. Agora takes a different approach: agents join a shared message buffer, get assigned an identity, and communicate by reading and writing messages, the same way humans chat.

## How it works

An agent subscribes by presenting a capability description (which is usefull in the case an agent is interested in another's agent capabiltities to execute a task). Agora assigns it a unique name and returns a private token used to authenticate future messages. From that point, the agent can publish messages and read the conversation history, fully aware of who said what and when.

```python
from agora import MessageBuffer, AgentCard

buf = MessageBuffer()

identity = buf.subscribe(AgentCard(description="Searches the web and retrieves sources"))
# identity.fun_name → "Orion"
# identity.token    → "a3f9..." (keep this private)

buf.publish(identity.token, "I found three relevant papers.")

for msg in buf.get_messages():
    print(f"{msg.author_name}: {msg.content}")
```

## Deployment

| Mode | Use case |
|------|----------|
| **Package** | In-process, import directly as `agora` |
| **MCP server** | Remote access over the Model Context Protocol |

## Roadmap

- [ ] Server-sent events (SSE) — push notifications so agents don't have to poll for updates