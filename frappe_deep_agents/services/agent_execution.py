"""
Agent Execution Service using LangGraph.
"""
import frappe
from typing import AsyncIterator, Union


class AgentExecutionService:
    """
    Execute Deep Agents using LangGraph.

    Handles:
    - Agent creation with tools and middlewares
    - Streaming execution
    - State management
    """

    def __init__(self, agent_definition: str, session_id: str):
        """
        Initialize execution service.

        Args:
            agent_definition: Agent Definition name
            session_id: Agent Session name
        """
        self.agent_def = frappe.get_doc("Agent Definition", agent_definition)
        self.session = frappe.get_doc("Agent Session", session_id)
        self.session_id = session_id

        # Initialize LLM
        from frappe_deep_agents.services.llm_service import LLMService

        provider = self.agent_def.llm_provider
        if provider == "Default":
            provider = None

        model = self.agent_def.llm_model or None

        self.llm_service = LLMService(provider=provider, model=model)
        self.llm = self.llm_service.get_langchain_llm()

        # Initialize sandbox if enabled
        self.sandbox = None
        if self.agent_def.enable_filesystem and self.session.sandbox_pod:
            from frappe_deep_agents.services.sandbox_service import SandboxService
            self.sandbox = SandboxService()

    def _build_tools(self) -> list:
        """Build LangChain tools based on agent configuration."""
        from frappe_deep_agents.tools import get_tools_for_agent

        return get_tools_for_agent(
            agent_def=self.agent_def,
            session_id=self.session_id,
            sandbox=self.sandbox,
            sandbox_pod=self.session.sandbox_pod
        )

    def _get_system_prompt(self) -> str:
        """Get system prompt for the agent."""
        base_prompt = self.agent_def.system_prompt or ""

        # Add tool usage instructions
        tool_instructions = """

You have access to tools to help complete tasks. Use them when needed.
For file operations, paths are relative to /workspace.
Keep track of progress using todos when working on multi-step tasks.
"""

        return base_prompt + tool_instructions

    def build_agent(self):
        """
        Build LangGraph agent with configured tools.

        Returns:
            Compiled LangGraph agent
        """
        from langgraph.prebuilt import create_react_agent

        tools = self._build_tools()
        system_prompt = self._get_system_prompt()

        # Create agent using LangGraph's prebuilt ReAct agent
        agent = create_react_agent(
            model=self.llm,
            tools=tools,
            state_modifier=system_prompt
        )

        return agent

    async def run(self, message: str) -> AsyncIterator[Union[str, dict]]:
        """
        Execute agent with user message, streaming response.

        Args:
            message: User message to process

        Yields:
            String tokens or dict with tool execution results
        """
        agent = self.build_agent()

        # Build input state
        input_state = {
            "messages": [
                {"role": "user", "content": message}
            ]
        }

        # Stream events
        async for event in agent.astream_events(
            input_state,
            version="v2"
        ):
            event_type = event.get("event")

            if event_type == "on_chat_model_stream":
                # Streaming token from LLM
                chunk = event.get("data", {}).get("chunk")
                if chunk and hasattr(chunk, "content") and chunk.content:
                    yield chunk.content

            elif event_type == "on_tool_start":
                # Tool execution starting
                tool_name = event.get("name", "unknown")
                yield {
                    "type": "tool_start",
                    "tool": tool_name,
                    "input": event.get("data", {}).get("input")
                }

            elif event_type == "on_tool_end":
                # Tool execution completed
                tool_name = event.get("name", "unknown")
                output = event.get("data", {}).get("output")

                yield {
                    "type": "tool_end",
                    "tool": tool_name,
                    "result": str(output) if output else ""
                }

                # Sync todos if todo tool was used
                if tool_name in ["write_todos", "update_todo"]:
                    self._sync_todos()

                # Sync files if file tool was used
                if tool_name in ["write_file", "edit_file"]:
                    self._sync_files()

    def _sync_todos(self):
        """Sync todos from agent state to database."""
        try:
            from frappe_deep_agents.tasks import sync_todos

            # Get todos from session state or agent state
            # This depends on how todos are tracked in the agent
            todos = getattr(self, "_current_todos", [])
            if todos:
                sync_todos(self.session_id, todos)
        except Exception as e:
            frappe.log_error(
                title="Todo sync failed",
                message=str(e)
            )

    def _sync_files(self):
        """Sync files from sandbox to database."""
        try:
            if self.sandbox and self.session.sandbox_pod:
                files = self.sandbox.list_files(self.session.sandbox_pod)
                from frappe_deep_agents.tasks import sync_files
                sync_files(self.session_id, files)
        except Exception as e:
            frappe.log_error(
                title="File sync failed",
                message=str(e)
            )

    def run_sync(self, message: str) -> str:
        """
        Synchronous execution (non-streaming).

        Args:
            message: User message to process

        Returns:
            Complete response string
        """
        import asyncio

        async def collect_response():
            full_response = ""
            async for chunk in self.run(message):
                if isinstance(chunk, str):
                    full_response += chunk
            return full_response

        return asyncio.run(collect_response())


def get_execution_service(
    agent_definition: str,
    session_id: str
) -> AgentExecutionService:
    """
    Factory function to get execution service.

    Args:
        agent_definition: Agent Definition name
        session_id: Agent Session name

    Returns:
        Configured AgentExecutionService instance
    """
    return AgentExecutionService(
        agent_definition=agent_definition,
        session_id=session_id
    )
