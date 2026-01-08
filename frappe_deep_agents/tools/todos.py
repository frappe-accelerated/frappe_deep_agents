"""
Todo management tools for tracking agent progress.
"""
import frappe
from typing import Optional, List
from langchain_core.tools import BaseTool
from pydantic import Field
import json


class WriteTodosTool(BaseTool):
    """Update the todo list for tracking task progress."""

    name: str = "write_todos"
    description: str = """Update the todo list. Provide a list of todos with:
- content: Description of the task
- status: One of "pending", "in_progress", "completed"

Example: [{"content": "Read config file", "status": "completed"}, {"content": "Update settings", "status": "in_progress"}]"""

    sandbox: Optional[object] = Field(default=None, exclude=True)
    sandbox_pod: Optional[str] = Field(default=None, exclude=True)
    session_id: Optional[str] = Field(default=None, exclude=True)

    def __init__(self, sandbox=None, sandbox_pod=None, session_id=None, **kwargs):
        super().__init__(**kwargs)
        self.sandbox = sandbox
        self.sandbox_pod = sandbox_pod
        self.session_id = session_id

    def _run(self, todos: str) -> str:
        """
        Update todo list.

        Args:
            todos: JSON string or list of todo items

        Returns:
            Confirmation message
        """
        if not self.session_id:
            return "Error: No session context"

        try:
            # Parse todos
            if isinstance(todos, str):
                todo_list = json.loads(todos)
            else:
                todo_list = todos

            if not isinstance(todo_list, list):
                return "Error: todos must be a list"

            # Get existing todos
            existing = frappe.get_all(
                "Agent Todo",
                filters={"session": self.session_id},
                fields=["name", "description", "status"]
            )
            existing_map = {t["description"]: t for t in existing}

            updated = 0
            created = 0

            for item in todo_list:
                content = item.get("content", "")
                status = item.get("status", "pending")

                if not content:
                    continue

                # Validate status
                if status not in ["pending", "in_progress", "completed"]:
                    status = "pending"

                if content in existing_map:
                    # Update existing
                    doc = frappe.get_doc("Agent Todo", existing_map[content]["name"])
                    if doc.status != status:
                        doc.status = status
                        doc.save()
                        updated += 1
                else:
                    # Create new
                    doc = frappe.new_doc("Agent Todo")
                    doc.session = self.session_id
                    doc.description = content
                    doc.status = status
                    doc.insert()
                    created += 1

            frappe.db.commit()

            # Emit update event
            from frappe.realtime import emit_via_redis

            updated_todos = frappe.get_all(
                "Agent Todo",
                filters={"session": self.session_id},
                fields=["name", "description", "status"]
            )

            emit_via_redis(
                f"agent_session_{self.session_id}",
                "todo_update",
                {"session": self.session_id, "todos": updated_todos}
            )

            return f"Todo list updated: {created} created, {updated} updated"
        except json.JSONDecodeError:
            return "Error: Invalid JSON format for todos"
        except Exception as e:
            return f"Error updating todos: {str(e)}"


class ReadTodosTool(BaseTool):
    """Read the current todo list."""

    name: str = "read_todos"
    description: str = "Get the current todo list showing all tasks and their status."

    sandbox: Optional[object] = Field(default=None, exclude=True)
    sandbox_pod: Optional[str] = Field(default=None, exclude=True)
    session_id: Optional[str] = Field(default=None, exclude=True)

    def __init__(self, sandbox=None, sandbox_pod=None, session_id=None, **kwargs):
        super().__init__(**kwargs)
        self.sandbox = sandbox
        self.sandbox_pod = sandbox_pod
        self.session_id = session_id

    def _run(self) -> str:
        """
        Read current todo list.

        Returns:
            Formatted list of todos
        """
        if not self.session_id:
            return "Error: No session context"

        try:
            todos = frappe.get_all(
                "Agent Todo",
                filters={"session": self.session_id},
                fields=["description", "status"],
                order_by="creation asc"
            )

            if not todos:
                return "No todos in current list"

            # Format output
            lines = ["Current Todo List:", ""]

            status_icons = {
                "pending": "[ ]",
                "in_progress": "[>]",
                "completed": "[x]"
            }

            for todo in todos:
                icon = status_icons.get(todo["status"], "[ ]")
                lines.append(f"{icon} {todo['description']}")

            return "\n".join(lines)
        except Exception as e:
            return f"Error reading todos: {str(e)}"


class UpdateTodoTool(BaseTool):
    """Update a single todo item status."""

    name: str = "update_todo"
    description: str = "Update a single todo status. Provide the todo description and new status (pending/in_progress/completed)."

    sandbox: Optional[object] = Field(default=None, exclude=True)
    sandbox_pod: Optional[str] = Field(default=None, exclude=True)
    session_id: Optional[str] = Field(default=None, exclude=True)

    def __init__(self, sandbox=None, sandbox_pod=None, session_id=None, **kwargs):
        super().__init__(**kwargs)
        self.sandbox = sandbox
        self.sandbox_pod = sandbox_pod
        self.session_id = session_id

    def _run(self, description: str, status: str) -> str:
        """
        Update a todo item.

        Args:
            description: Todo description to find
            status: New status

        Returns:
            Confirmation message
        """
        if not self.session_id:
            return "Error: No session context"

        if status not in ["pending", "in_progress", "completed"]:
            return f"Error: Invalid status '{status}'. Use pending/in_progress/completed"

        try:
            # Find todo by description
            todo_name = frappe.db.get_value(
                "Agent Todo",
                {"session": self.session_id, "description": description},
                "name"
            )

            if not todo_name:
                return f"Error: Todo not found: {description}"

            doc = frappe.get_doc("Agent Todo", todo_name)
            doc.status = status
            doc.save()
            frappe.db.commit()

            # Emit update
            from frappe.realtime import emit_via_redis

            updated_todos = frappe.get_all(
                "Agent Todo",
                filters={"session": self.session_id},
                fields=["name", "description", "status"]
            )

            emit_via_redis(
                f"agent_session_{self.session_id}",
                "todo_update",
                {"session": self.session_id, "todos": updated_todos}
            )

            return f"Updated '{description}' to {status}"
        except Exception as e:
            return f"Error updating todo: {str(e)}"
