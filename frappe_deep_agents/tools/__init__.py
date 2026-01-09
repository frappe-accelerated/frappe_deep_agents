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
from frappe_deep_agents.tools.todos import WriteTodosTool, ReadTodosTool, UpdateTodoTool
from frappe_deep_agents.tools.frappe_tools import (
    FrappeQueryTool,
    FrappeGetDocTool,
    FrappeCreateDocTool,
    FrappeUpdateDocTool,
    FrappeDeleteDocTool,
    FrappeRunMethodTool
)
from frappe_deep_agents.tools.web_tools import WebSearchTool, WebFetchTool
from frappe_deep_agents.tools.python_tools import PythonREPLTool, PythonCalculatorTool


# Registry of all built-in tools
BUILTIN_TOOLS = {
    # Filesystem tools
    "read_file": ReadFileTool,
    "write_file": WriteFileTool,
    "edit_file": EditFileTool,

    # Search tools
    "glob": GlobTool,
    "grep": GrepTool,

    # Execution tools
    "bash": BashTool,
    "python_repl": PythonREPLTool,
    "calculator": PythonCalculatorTool,

    # Todo tools
    "write_todos": WriteTodosTool,
    "read_todos": ReadTodosTool,
    "update_todo": UpdateTodoTool,

    # Frappe tools
    "frappe_query": FrappeQueryTool,
    "frappe_get_doc": FrappeGetDocTool,
    "frappe_create_doc": FrappeCreateDocTool,
    "frappe_update_doc": FrappeUpdateDocTool,
    "frappe_delete_doc": FrappeDeleteDocTool,
    "frappe_run_method": FrappeRunMethodTool,

    # Web tools
    "web_search": WebSearchTool,
    "web_fetch": WebFetchTool,
}


def get_tool(
    name: str,
    sandbox=None,
    sandbox_pod: str = None,
    session_id: str = None
):
    """
    Get a tool instance configured for a session.

    Args:
        name: Tool name from BUILTIN_TOOLS
        sandbox: SandboxService instance (optional)
        sandbox_pod: Pod name for execution (optional)
        session_id: Agent Session name (optional)

    Returns:
        Configured tool instance

    Raises:
        ValueError if tool name is unknown
    """
    tool_class = BUILTIN_TOOLS.get(name)
    if not tool_class:
        raise ValueError(f"Unknown tool: {name}")

    # Build kwargs based on what the tool accepts
    kwargs = {}
    if session_id:
        kwargs['session_id'] = session_id
    if sandbox:
        kwargs['sandbox'] = sandbox
    if sandbox_pod:
        kwargs['sandbox_pod'] = sandbox_pod

    return tool_class(**kwargs)


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


def get_default_tools(session_id: str, sandbox=None, sandbox_pod: str = None) -> list:
    """
    Get a default set of commonly useful tools.

    Args:
        session_id: Agent Session name
        sandbox: Optional SandboxService instance
        sandbox_pod: Optional pod name

    Returns:
        List of default tool instances
    """
    default_tool_names = [
        "read_file", "write_file", "edit_file",
        "glob", "grep", "bash",
        "write_todos", "read_todos",
        "calculator"
    ]

    tools = []
    for name in default_tool_names:
        try:
            tool = get_tool(
                name=name,
                sandbox=sandbox,
                sandbox_pod=sandbox_pod,
                session_id=session_id
            )
            tools.append(tool)
        except ValueError:
            pass

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
            "description": (cls.__doc__ or "").strip().split('\n')[0]
        }
        for name, cls in BUILTIN_TOOLS.items()
    ]
