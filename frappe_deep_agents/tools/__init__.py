"""
Built-in tools for frappe_deep_agents.
"""
from typing import Optional
from frappe_deep_agents.tools.filesystem import (
    ReadFileTool,
    WriteFileTool,
    EditFileTool
)
from frappe_deep_agents.tools.search import GlobTool, GrepTool
from frappe_deep_agents.tools.bash import BashTool
from frappe_deep_agents.tools.todos import WriteTodosTool, ReadTodosTool


# Registry of all built-in tools
BUILTIN_TOOLS = {
    "read_file": ReadFileTool,
    "write_file": WriteFileTool,
    "edit_file": EditFileTool,
    "glob": GlobTool,
    "grep": GrepTool,
    "bash": BashTool,
    "write_todos": WriteTodosTool,
    "read_todos": ReadTodosTool,
}


def get_tool(
    name: str,
    sandbox,
    sandbox_pod: str,
    session_id: str
):
    """
    Get a tool instance configured for a session.

    Args:
        name: Tool name from BUILTIN_TOOLS
        sandbox: SandboxService instance
        sandbox_pod: Pod name for execution
        session_id: Agent Session name

    Returns:
        Configured tool instance

    Raises:
        ValueError if tool name is unknown
    """
    tool_class = BUILTIN_TOOLS.get(name)
    if not tool_class:
        raise ValueError(f"Unknown tool: {name}")

    return tool_class(
        sandbox=sandbox,
        sandbox_pod=sandbox_pod,
        session_id=session_id
    )


def get_tools_for_agent(
    agent_def,
    session_id: str,
    sandbox=None,
    sandbox_pod: str = None
) -> list:
    """
    Get all enabled tools for an agent.

    Args:
        agent_def: Agent Definition document
        session_id: Agent Session name
        sandbox: Optional SandboxService instance
        sandbox_pod: Optional pod name

    Returns:
        List of LangChain tool instances
    """
    tools = []

    for tool_row in agent_def.tools:
        if not tool_row.enabled:
            continue

        tool_name = tool_row.tool_name
        tool_type = tool_row.tool_type or "builtin"

        if tool_type == "builtin":
            try:
                tool = get_tool(
                    name=tool_name,
                    sandbox=sandbox,
                    sandbox_pod=sandbox_pod,
                    session_id=session_id
                )
                tools.append(tool)
            except ValueError:
                # Unknown tool, skip
                pass

        # TODO: Support MCP and custom tools

    return tools


def list_available_tools() -> list:
    """
    List all available built-in tools.

    Returns:
        List of tool info dicts
    """
    return [
        {
            "name": name,
            "type": "builtin",
            "description": cls.__doc__ or ""
        }
        for name, cls in BUILTIN_TOOLS.items()
    ]
