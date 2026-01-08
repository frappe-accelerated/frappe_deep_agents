"""
Search tools for finding files and content in sandbox.
"""
from typing import Optional
from langchain_core.tools import BaseTool
from pydantic import Field


class GlobTool(BaseTool):
    """Find files matching a glob pattern."""

    name: str = "glob"
    description: str = "Find files matching a glob pattern in the workspace. Examples: '*.py', 'src/**/*.ts', '**/*.json'"

    sandbox: Optional[object] = Field(default=None, exclude=True)
    sandbox_pod: Optional[str] = Field(default=None, exclude=True)
    session_id: Optional[str] = Field(default=None, exclude=True)

    def __init__(self, sandbox=None, sandbox_pod=None, session_id=None, **kwargs):
        super().__init__(**kwargs)
        self.sandbox = sandbox
        self.sandbox_pod = sandbox_pod
        self.session_id = session_id

    def _run(self, pattern: str, path: str = "") -> str:
        """
        Find files matching glob pattern.

        Args:
            pattern: Glob pattern to match
            path: Optional subdirectory to search in

        Returns:
            List of matching file paths
        """
        if not self.sandbox or not self.sandbox_pod:
            return "Error: Sandbox not available"

        try:
            # Use find command with glob pattern
            search_path = f"/workspace/{path.lstrip('/')}" if path else "/workspace"

            # Convert glob to find pattern
            cmd = ["find", search_path, "-type", "f", "-name", pattern]

            result = self.sandbox.exec_command(self.sandbox_pod, cmd)

            if not result or result.startswith("Error"):
                return f"No files found matching '{pattern}'"

            # Clean up paths
            files = []
            for line in result.strip().split("\n"):
                if line:
                    # Remove /workspace prefix for cleaner output
                    clean_path = line.replace("/workspace/", "")
                    files.append(clean_path)

            if not files:
                return f"No files found matching '{pattern}'"

            return "\n".join(files)
        except Exception as e:
            return f"Error searching files: {str(e)}"


class GrepTool(BaseTool):
    """Search for text patterns in files."""

    name: str = "grep"
    description: str = "Search for a text pattern in files. Supports regex. Provide pattern and optional path to search in."

    sandbox: Optional[object] = Field(default=None, exclude=True)
    sandbox_pod: Optional[str] = Field(default=None, exclude=True)
    session_id: Optional[str] = Field(default=None, exclude=True)

    def __init__(self, sandbox=None, sandbox_pod=None, session_id=None, **kwargs):
        super().__init__(**kwargs)
        self.sandbox = sandbox
        self.sandbox_pod = sandbox_pod
        self.session_id = session_id

    def _run(self, pattern: str, path: str = "", include: str = "") -> str:
        """
        Search for pattern in files.

        Args:
            pattern: Text or regex pattern to search
            path: Optional subdirectory to search in
            include: Optional file pattern to include (e.g., "*.py")

        Returns:
            Matching lines with file paths
        """
        if not self.sandbox or not self.sandbox_pod:
            return "Error: Sandbox not available"

        try:
            search_path = f"/workspace/{path.lstrip('/')}" if path else "/workspace"

            # Build grep command
            cmd = ["grep", "-r", "-n", "--color=never"]

            if include:
                cmd.extend(["--include", include])

            cmd.extend([pattern, search_path])

            result = self.sandbox.exec_command(self.sandbox_pod, cmd)

            if not result or "No such file" in result:
                return f"No matches found for '{pattern}'"

            # Clean up output
            lines = []
            for line in result.strip().split("\n"):
                if line:
                    # Remove /workspace prefix
                    clean_line = line.replace("/workspace/", "")
                    lines.append(clean_line)

            if not lines:
                return f"No matches found for '{pattern}'"

            # Limit output
            if len(lines) > 50:
                lines = lines[:50]
                lines.append(f"... and more matches (showing first 50)")

            return "\n".join(lines)
        except Exception as e:
            return f"Error searching: {str(e)}"
