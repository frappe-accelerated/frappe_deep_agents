# Frappe Deep Agents

LangChain Deep Agents implementation for Frappe with Kubernetes sandbox support.

## Features

- **LLM Providers**: OpenRouter and Ollama support
- **Kubernetes Sandbox**: Isolated pod execution with filesystem access
- **Built-in Tools**: File operations, search, bash execution, todo tracking
- **Real-time Streaming**: Socket.IO based token streaming
- **Vue.js UI**: Embedded in Frappe Desk
- **YAML Configuration**: Export/import agent definitions

## Installation

```bash
cd frappe-bench
bench get-app https://github.com/your-repo/frappe_deep_agents
bench --site your-site install-app frappe_deep_agents
bench --site your-site migrate
```

## Configuration

1. Go to **Deep Agent Settings** in Frappe Desk
2. Configure LLM provider (OpenRouter or Ollama)
3. Set up Kubernetes namespace for sandbox pods

## Creating an Agent

1. Go to **Agent Definition** > New
2. Set agent name and system prompt
3. Enable desired features (filesystem, todos, subagents)
4. Add tools from the built-in list
5. Save

## API Usage

```python
import frappe

# Create a session
result = frappe.call('frappe_deep_agents.api.create_session', agent_definition='my-agent')
session_id = result['session']

# Send a message (async, streams via Socket.IO)
frappe.call('frappe_deep_agents.api.send_message', session_id=session_id, message='Hello!')

# Get session details
session = frappe.call('frappe_deep_agents.api.get_session', session_id=session_id)
```

## Built-in Tools

| Tool | Description |
|------|-------------|
| read_file | Read file from sandbox |
| write_file | Write file to sandbox |
| edit_file | Edit file with replacement |
| glob | Find files by pattern |
| grep | Search file contents |
| bash | Execute shell commands |
| write_todos | Update todo list |
| read_todos | Get current todos |

## Dependencies

- frappe >= 15.0.0
- langchain >= 0.3
- langgraph >= 0.2
- kubernetes >= 29.0.0

## License

MIT
