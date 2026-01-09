"""
Real-time Socket.IO event management for Deep Agents.

Provides consistent event emission for all agent activities.
"""
import frappe
from frappe.realtime import emit_via_redis


def emit_tool_call_start(session_id: str, tool_name: str, tool_input: dict):
    """
    Emit event when a tool call starts.

    Args:
        session_id: Agent Session name
        tool_name: Name of the tool being called
        tool_input: Input parameters for the tool
    """
    emit_via_redis(
        f"agent_session_{session_id}",
        "tool_call_start",
        {
            "session": session_id,
            "tool_name": tool_name,
            "input": tool_input,
            "status": "running"
        }
    )


def emit_tool_call_complete(session_id: str, tool_name: str, output: str, success: bool = True):
    """
    Emit event when a tool call completes.

    Args:
        session_id: Agent Session name
        tool_name: Name of the tool that completed
        output: Tool execution result
        success: Whether the tool executed successfully
    """
    emit_via_redis(
        f"agent_session_{session_id}",
        "tool_call_complete",
        {
            "session": session_id,
            "tool_name": tool_name,
            "output": output,
            "success": success,
            "status": "completed" if success else "error"
        }
    )


def emit_agent_token(session_id: str, token: str):
    """
    Emit a streaming token from the agent.

    Args:
        session_id: Agent Session name
        token: Token to emit
    """
    emit_via_redis(
        f"agent_session_{session_id}",
        "agent_token",
        {
            "session": session_id,
            "token": token
        }
    )


def emit_file_update(session_id: str, files: list):
    """
    Emit event when files are created or modified.

    Args:
        session_id: Agent Session name
        files: List of file info dicts
    """
    emit_via_redis(
        f"agent_session_{session_id}",
        "file_update",
        {
            "session": session_id,
            "files": files
        }
    )


def emit_todo_update(session_id: str, todos: list):
    """
    Emit event when todos are updated.

    Args:
        session_id: Agent Session name
        todos: List of todo info dicts
    """
    emit_via_redis(
        f"agent_session_{session_id}",
        "todo_update",
        {
            "session": session_id,
            "todos": todos
        }
    )


def emit_agent_complete(session_id: str, status: str = "success"):
    """
    Emit event when agent execution completes.

    Args:
        session_id: Agent Session name
        status: Completion status
    """
    emit_via_redis(
        f"agent_session_{session_id}",
        "agent_complete",
        {
            "session": session_id,
            "status": status
        }
    )


def emit_agent_error(session_id: str, error: str):
    """
    Emit event when an error occurs.

    Args:
        session_id: Agent Session name
        error: Error message
    """
    emit_via_redis(
        f"agent_session_{session_id}",
        "agent_error",
        {
            "session": session_id,
            "error": error
        }
    )


def emit_agent_status(session_id: str, status: str, message: str = ""):
    """
    Emit agent status update.

    Args:
        session_id: Agent Session name
        status: Status string (thinking, working, idle)
        message: Optional status message
    """
    emit_via_redis(
        f"agent_session_{session_id}",
        "agent_status",
        {
            "session": session_id,
            "status": status,
            "message": message
        }
    )
