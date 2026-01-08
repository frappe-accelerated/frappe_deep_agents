"""
Bash tool for executing shell commands in sandbox.
"""
from typing import Optional
from langchain_core.tools import BaseTool
from pydantic import Field


class BashTool(BaseTool):
    """Execute shell commands in the workspace."""

    name: str = "bash"
    description: str = "Execute a shell command in the workspace. Use for running scripts, installing packages, or system operations."

    sandbox: Optional[object] = Field(default=None, exclude=True)
    sandbox_pod: Optional[str] = Field(default=None, exclude=True)
    session_id: Optional[str] = Field(default=None, exclude=True)

    # Commands that are blocked for safety
    BLOCKED_COMMANDS = [
        "rm -rf /",
        "rm -rf /*",
        "mkfs",
        "dd if=",
        ":(){:|:&};:",  # Fork bomb
        "chmod -R 777 /",
        "chown -R",
    ]

    def __init__(self, sandbox=None, sandbox_pod=None, session_id=None, **kwargs):
        super().__init__(**kwargs)
        self.sandbox = sandbox
        self.sandbox_pod = sandbox_pod
        self.session_id = session_id

    def _run(self, command: str, timeout: int = 30) -> str:
        """
        Execute shell command.

        Args:
            command: Shell command to execute
            timeout: Execution timeout in seconds (default 30)

        Returns:
            Command output (stdout + stderr)
        """
        if not self.sandbox or not self.sandbox_pod:
            return "Error: Sandbox not available"

        # Safety check
        for blocked in self.BLOCKED_COMMANDS:
            if blocked in command:
                return f"Error: Command contains blocked pattern: {blocked}"

        try:
            # Execute command via bash
            result = self.sandbox.exec_command(
                self.sandbox_pod,
                ["bash", "-c", f"cd /workspace && {command}"],
                timeout=timeout
            )

            if not result:
                return "Command completed with no output"

            # Truncate very long output
            if len(result) > 10000:
                result = result[:10000] + "\n... (output truncated)"

            return result
        except Exception as e:
            return f"Error executing command: {str(e)}"


class PythonTool(BaseTool):
    """Execute Python code in the workspace."""

    name: str = "python"
    description: str = "Execute Python code in the workspace. Provide the code to run."

    sandbox: Optional[object] = Field(default=None, exclude=True)
    sandbox_pod: Optional[str] = Field(default=None, exclude=True)
    session_id: Optional[str] = Field(default=None, exclude=True)

    def __init__(self, sandbox=None, sandbox_pod=None, session_id=None, **kwargs):
        super().__init__(**kwargs)
        self.sandbox = sandbox
        self.sandbox_pod = sandbox_pod
        self.session_id = session_id

    def _run(self, code: str) -> str:
        """
        Execute Python code.

        Args:
            code: Python code to execute

        Returns:
            Execution output
        """
        if not self.sandbox or not self.sandbox_pod:
            return "Error: Sandbox not available"

        try:
            # Write code to temp file and execute
            temp_file = "/workspace/.temp_script.py"

            # Write the script
            self.sandbox.write_file(self.sandbox_pod, ".temp_script.py", code)

            # Execute
            result = self.sandbox.exec_command(
                self.sandbox_pod,
                ["python3", temp_file],
                timeout=60
            )

            # Clean up
            self.sandbox.exec_command(
                self.sandbox_pod,
                ["rm", "-f", temp_file]
            )

            return result if result else "Code executed with no output"
        except Exception as e:
            return f"Error executing Python: {str(e)}"
