"""
Background tasks for frappe_deep_agents.
"""
import frappe
from frappe.realtime import emit_via_redis


def run_agent(session_id: str, message: str):
    """
    Run agent in background, streaming tokens via Socket.IO.

    Args:
        session_id: Agent Session name
        message: User message to process
    """
    try:
        session = frappe.get_doc("Agent Session", session_id)
        agent_def = frappe.get_doc("Agent Definition", session.agent_definition)

        # Import execution service
        from frappe_deep_agents.services.agent_execution import AgentExecutionService

        service = AgentExecutionService(
            agent_definition=session.agent_definition,
            session_id=session_id
        )

        full_response = ""

        # Run agent with streaming
        import asyncio

        async def stream_agent():
            nonlocal full_response
            async for chunk in service.run(message):
                if isinstance(chunk, str):
                    full_response += chunk
                    # Emit token to client
                    emit_via_redis(
                        f"agent_session_{session_id}",
                        "agent_token",
                        {"token": chunk, "session": session_id}
                    )
                elif isinstance(chunk, dict):
                    # Tool execution result
                    emit_via_redis(
                        f"agent_session_{session_id}",
                        "tool_result",
                        {
                            "tool": chunk.get("tool"),
                            "result": chunk.get("result"),
                            "session": session_id
                        }
                    )

        asyncio.run(stream_agent())

        # Save final response
        session.reload()
        session.append("messages", {
            "role": "assistant",
            "content": full_response
        })
        session.save()

        # Emit completion event
        emit_via_redis(
            f"agent_session_{session_id}",
            "agent_complete",
            {"session": session_id, "status": "success"}
        )

        frappe.db.commit()

    except Exception as e:
        frappe.log_error(
            title=f"Agent execution failed: {session_id}",
            message=str(e)
        )

        # Emit error event
        emit_via_redis(
            f"agent_session_{session_id}",
            "agent_error",
            {"session": session_id, "error": str(e)}
        )

        # Update session status
        try:
            session = frappe.get_doc("Agent Session", session_id)
            session.status = "error"
            session.save()
            frappe.db.commit()
        except Exception:
            pass


def cleanup_sessions():
    """
    Cleanup old/stale sessions and their sandboxes.

    Run hourly to:
    - Mark inactive sessions as timed out
    - Cleanup sandbox pods for completed/error sessions
    """
    from datetime import datetime, timedelta

    try:
        settings = frappe.get_single("Deep Agent Settings")
        timeout_minutes = settings.sandbox_timeout_minutes or 30
    except Exception:
        timeout_minutes = 30

    cutoff = datetime.now() - timedelta(minutes=timeout_minutes)

    # Find stale active sessions
    stale_sessions = frappe.get_all(
        "Agent Session",
        filters={
            "status": "active",
            "creation": ["<", cutoff]
        },
        pluck="name"
    )

    for session_id in stale_sessions:
        try:
            session = frappe.get_doc("Agent Session", session_id)
            session.status = "timeout"
            session.save()

            # Cleanup sandbox
            if session.sandbox_pod:
                try:
                    from frappe_deep_agents.services.sandbox_service import SandboxService
                    sandbox = SandboxService()
                    sandbox.cleanup_sandbox(session_id)
                except Exception as e:
                    frappe.log_error(
                        title=f"Sandbox cleanup failed: {session_id}",
                        message=str(e)
                    )

            frappe.db.commit()
        except Exception as e:
            frappe.log_error(
                title=f"Session cleanup failed: {session_id}",
                message=str(e)
            )


def sync_todos(session_id: str, todos: list):
    """
    Sync todo list from agent middleware to database.

    Args:
        session_id: Agent Session name
        todos: List of todo items from agent
    """
    # Get existing todos
    existing = frappe.get_all(
        "Agent Todo",
        filters={"session": session_id},
        fields=["name", "description"]
    )
    existing_map = {t["description"]: t["name"] for t in existing}

    for todo in todos:
        desc = todo.get("content") or todo.get("description")
        status = todo.get("status", "pending")

        if desc in existing_map:
            # Update existing
            doc = frappe.get_doc("Agent Todo", existing_map[desc])
            doc.status = status
            doc.save()
        else:
            # Create new
            doc = frappe.new_doc("Agent Todo")
            doc.session = session_id
            doc.description = desc
            doc.status = status
            doc.insert()

    frappe.db.commit()

    # Emit update event
    updated_todos = frappe.get_all(
        "Agent Todo",
        filters={"session": session_id},
        fields=["name", "description", "status"]
    )

    emit_via_redis(
        f"agent_session_{session_id}",
        "todo_update",
        {"session": session_id, "todos": updated_todos}
    )


def sync_files(session_id: str, files: list):
    """
    Sync file list from sandbox to database.

    Args:
        session_id: Agent Session name
        files: List of file info from sandbox
    """
    for file_info in files:
        file_path = file_info.get("path")

        # Check if exists
        existing = frappe.db.exists("Agent File", {
            "session": session_id,
            "file_path": file_path
        })

        if not existing:
            doc = frappe.new_doc("Agent File")
            doc.session = session_id
            doc.file_path = file_path
            doc.is_directory = file_info.get("is_directory", False)
            doc.content = file_info.get("content", "")
            doc.insert()

    frappe.db.commit()

    # Emit update event
    updated_files = frappe.get_all(
        "Agent File",
        filters={"session": session_id},
        fields=["name", "file_path", "is_directory"]
    )

    emit_via_redis(
        f"agent_session_{session_id}",
        "file_update",
        {"session": session_id, "files": updated_files}
    )
