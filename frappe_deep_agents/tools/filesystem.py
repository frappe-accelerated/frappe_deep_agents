"""
Filesystem tools for reading, writing, and editing files in sandbox.
"""
from typing import Optional
from langchain_core.tools import BaseTool
from pydantic import Field


class ReadFileTool(BaseTool):
    """Read contents of a file from the workspace."""

    name: str = "read_file"
    description: str = "Read the contents of a file from the workspace. Provide the file path relative to /workspace."

    sandbox: Optional[object] = Field(default=None, exclude=True)
    sandbox_pod: Optional[str] = Field(default=None, exclude=True)
    session_id: Optional[str] = Field(default=None, exclude=True)

    def __init__(self, sandbox=None, sandbox_pod=None, session_id=None, **kwargs):
        super().__init__(**kwargs)
        self.sandbox = sandbox
        self.sandbox_pod = sandbox_pod
        self.session_id = session_id

    def _run(self, file_path: str) -> str:
        """
        Read file from sandbox.

        Args:
            file_path: Path relative to /workspace

        Returns:
            File contents
        """
        if not self.sandbox or not self.sandbox_pod:
            return "Error: Sandbox not available"

        try:
            content = self.sandbox.read_file(self.sandbox_pod, file_path)
            return content
        except Exception as e:
            return f"Error reading file: {str(e)}"


class WriteFileTool(BaseTool):
    """Write content to a file in the workspace."""

    name: str = "write_file"
    description: str = "Write content to a file in the workspace. Creates parent directories if needed. Provide file_path and content."

    sandbox: Optional[object] = Field(default=None, exclude=True)
    sandbox_pod: Optional[str] = Field(default=None, exclude=True)
    session_id: Optional[str] = Field(default=None, exclude=True)

    def __init__(self, sandbox=None, sandbox_pod=None, session_id=None, **kwargs):
        super().__init__(**kwargs)
        self.sandbox = sandbox
        self.sandbox_pod = sandbox_pod
        self.session_id = session_id

    def _run(self, file_path: str, content: str) -> str:
        """
        Write file to sandbox.

        Args:
            file_path: Path relative to /workspace
            content: Content to write

        Returns:
            Status message
        """
        if not self.sandbox or not self.sandbox_pod:
            return "Error: Sandbox not available"

        try:
            result = self.sandbox.write_file(self.sandbox_pod, file_path, content)

            # Sync to database
            self._sync_file(file_path, content)

            return result
        except Exception as e:
            return f"Error writing file: {str(e)}"

    def _sync_file(self, file_path: str, content: str):
        """Sync file to Agent File doctype."""
        import frappe

        try:
            existing = frappe.db.exists("Agent File", {
                "session": self.session_id,
                "file_path": file_path
            })

            if existing:
                doc = frappe.get_doc("Agent File", existing)
                doc.content = content
                doc.save()
            else:
                doc = frappe.new_doc("Agent File")
                doc.session = self.session_id
                doc.file_path = file_path
                doc.content = content
                doc.is_directory = False
                doc.insert()

            frappe.db.commit()
        except Exception:
            pass  # Non-critical


class EditFileTool(BaseTool):
    """Edit a file by replacing old text with new text."""

    name: str = "edit_file"
    description: str = "Edit a file by replacing specific text. Provide file_path, old_string (text to find), and new_string (replacement text)."

    sandbox: Optional[object] = Field(default=None, exclude=True)
    sandbox_pod: Optional[str] = Field(default=None, exclude=True)
    session_id: Optional[str] = Field(default=None, exclude=True)

    def __init__(self, sandbox=None, sandbox_pod=None, session_id=None, **kwargs):
        super().__init__(**kwargs)
        self.sandbox = sandbox
        self.sandbox_pod = sandbox_pod
        self.session_id = session_id

    def _run(self, file_path: str, old_string: str, new_string: str) -> str:
        """
        Edit file by replacing text.

        Args:
            file_path: Path relative to /workspace
            old_string: Text to find and replace
            new_string: Replacement text

        Returns:
            Status message
        """
        if not self.sandbox or not self.sandbox_pod:
            return "Error: Sandbox not available"

        try:
            # Read current content
            content = self.sandbox.read_file(self.sandbox_pod, file_path)

            if old_string not in content:
                return f"Error: old_string not found in {file_path}"

            # Count occurrences
            count = content.count(old_string)
            if count > 1:
                return f"Error: old_string found {count} times. Please provide more context to make it unique."

            # Replace
            new_content = content.replace(old_string, new_string)

            # Write back
            self.sandbox.write_file(self.sandbox_pod, file_path, new_content)

            # Sync to database
            self._sync_file(file_path, new_content)

            return f"Successfully edited {file_path}"
        except Exception as e:
            return f"Error editing file: {str(e)}"

    def _sync_file(self, file_path: str, content: str):
        """Sync file to Agent File doctype."""
        import frappe

        try:
            existing = frappe.db.exists("Agent File", {
                "session": self.session_id,
                "file_path": file_path
            })

            if existing:
                doc = frappe.get_doc("Agent File", existing)
                doc.content = content
                doc.save()
            else:
                doc = frappe.new_doc("Agent File")
                doc.session = self.session_id
                doc.file_path = file_path
                doc.content = content
                doc.is_directory = False
                doc.insert()

            frappe.db.commit()
        except Exception:
            pass  # Non-critical
