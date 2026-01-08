"""
Public API endpoints for frappe_deep_agents.
"""
import frappe
from frappe import _


@frappe.whitelist()
def create_session(agent_definition: str) -> dict:
    """
    Create a new agent session.

    Args:
        agent_definition: Name of the Agent Definition to use

    Returns:
        dict with session name and status
    """
    agent = frappe.get_doc("Agent Definition", agent_definition)

    session = frappe.new_doc("Agent Session")
    session.agent_definition = agent_definition
    session.status = "active"
    session.insert()

    # Create sandbox if filesystem is enabled
    if agent.enable_filesystem:
        try:
            from frappe_deep_agents.services.sandbox_service import SandboxService
            sandbox = SandboxService()
            sandbox_info = sandbox.create_sandbox(session.name)
            session.sandbox_pod = sandbox_info.get("pod_name")
            session.save()
        except Exception as e:
            frappe.log_error(
                title="Failed to create sandbox",
                message=str(e)
            )

    frappe.db.commit()

    return {
        "session": session.name,
        "agent": agent_definition,
        "status": "active"
    }


@frappe.whitelist()
def send_message(session_id: str, message: str) -> dict:
    """
    Send a message to an agent session.

    The message is processed asynchronously and responses
    are streamed via Socket.IO.

    Args:
        session_id: Agent Session name
        message: User message content

    Returns:
        dict with processing status
    """
    session = frappe.get_doc("Agent Session", session_id)

    if session.status != "active":
        frappe.throw(_("Session is not active"))

    # Add user message to session
    session.append("messages", {
        "role": "user",
        "content": message
    })
    session.save()
    frappe.db.commit()

    # Enqueue background processing
    frappe.enqueue(
        "frappe_deep_agents.tasks.run_agent",
        queue="long",
        timeout=1800,  # 30 minutes
        session_id=session_id,
        message=message
    )

    return {"status": "processing", "session": session_id}


@frappe.whitelist()
def get_session(session_id: str) -> dict:
    """
    Get session details with messages, todos, and files.

    Args:
        session_id: Agent Session name

    Returns:
        Session data with related documents
    """
    session = frappe.get_doc("Agent Session", session_id)

    # Get todos
    todos = frappe.get_all(
        "Agent Todo",
        filters={"session": session_id},
        fields=["name", "description", "status", "creation"]
    )

    # Get files
    files = frappe.get_all(
        "Agent File",
        filters={"session": session_id},
        fields=["name", "file_path", "is_directory", "creation"]
    )

    return {
        "name": session.name,
        "agent_definition": session.agent_definition,
        "status": session.status,
        "messages": [
            {
                "role": m.role,
                "content": m.content,
                "tool_name": m.tool_name,
                "creation": str(m.creation) if hasattr(m, "creation") else None
            }
            for m in session.messages
        ],
        "todos": todos,
        "files": files,
        "started_at": str(session.started_at) if session.started_at else None
    }


@frappe.whitelist()
def end_session(session_id: str) -> dict:
    """
    End an agent session and cleanup sandbox.

    Args:
        session_id: Agent Session name

    Returns:
        dict with completion status
    """
    session = frappe.get_doc("Agent Session", session_id)
    session.status = "completed"
    session.save()

    # Cleanup sandbox
    if session.sandbox_pod:
        try:
            from frappe_deep_agents.services.sandbox_service import SandboxService
            sandbox = SandboxService()
            sandbox.cleanup_sandbox(session_id)
        except Exception as e:
            frappe.log_error(
                title="Failed to cleanup sandbox",
                message=str(e)
            )

    frappe.db.commit()
    return {"status": "completed", "session": session_id}


@frappe.whitelist()
def list_agents() -> list:
    """
    List available agent definitions.

    Returns:
        List of agent definitions with basic info
    """
    agents = frappe.get_all(
        "Agent Definition",
        fields=["name", "agent_name", "description", "enable_filesystem", "enable_todos"]
    )
    return agents


@frappe.whitelist()
def list_sessions(agent_definition: str = None, status: str = None) -> list:
    """
    List sessions, optionally filtered by agent or status.

    Args:
        agent_definition: Filter by agent
        status: Filter by status (active, completed, error)

    Returns:
        List of sessions
    """
    filters = {}
    if agent_definition:
        filters["agent_definition"] = agent_definition
    if status:
        filters["status"] = status

    sessions = frappe.get_all(
        "Agent Session",
        filters=filters,
        fields=["name", "agent_definition", "status", "started_at", "creation"],
        order_by="creation desc",
        limit=50
    )
    return sessions


@frappe.whitelist()
def update_todo(todo_name: str, status: str) -> dict:
    """
    Update a todo item status.

    Args:
        todo_name: Agent Todo name
        status: New status (pending, in_progress, completed)

    Returns:
        Updated todo data
    """
    todo = frappe.get_doc("Agent Todo", todo_name)
    todo.status = status
    todo.save()
    frappe.db.commit()

    return {
        "name": todo.name,
        "description": todo.description,
        "status": todo.status
    }


@frappe.whitelist()
def export_agent_yaml(agent_definition: str) -> str:
    """
    Export agent definition as YAML.

    Args:
        agent_definition: Agent Definition name

    Returns:
        YAML string
    """
    from frappe_deep_agents.services.yaml_service import YAMLService
    return YAMLService.export_agent(agent_definition)


@frappe.whitelist()
def import_agent_yaml(yaml_content: str) -> dict:
    """
    Import agent definition from YAML.

    Args:
        yaml_content: YAML string

    Returns:
        dict with imported agent name
    """
    from frappe_deep_agents.services.yaml_service import YAMLService
    agent_name = YAMLService.import_agent(yaml_content)
    return {"agent": agent_name, "status": "imported"}
