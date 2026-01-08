# Copyright (c) 2025, Frappe Accelerated and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AgentDefinition(Document):
    def validate(self):
        # Ensure agent_name is valid
        if self.agent_name:
            self.agent_name = self.agent_name.strip().lower().replace(" ", "-")

    def before_save(self):
        # Auto-generate YAML config
        if not self.yaml_config:
            self.yaml_config = self.export_yaml()

    def export_yaml(self):
        """Export this agent definition as YAML."""
        from frappe_deep_agents.services.yaml_service import YAMLService
        return YAMLService.export_agent(self.name)

    def add_default_tools(self):
        """Add default set of tools to the agent."""
        default_tools = [
            {"tool_name": "read_file", "tool_type": "builtin", "enabled": 1},
            {"tool_name": "write_file", "tool_type": "builtin", "enabled": 1},
            {"tool_name": "edit_file", "tool_type": "builtin", "enabled": 1},
            {"tool_name": "glob", "tool_type": "builtin", "enabled": 1},
            {"tool_name": "grep", "tool_type": "builtin", "enabled": 1},
            {"tool_name": "bash", "tool_type": "builtin", "enabled": 1},
        ]

        if self.enable_todos:
            default_tools.extend([
                {"tool_name": "write_todos", "tool_type": "builtin", "enabled": 1},
                {"tool_name": "read_todos", "tool_type": "builtin", "enabled": 1},
            ])

        for tool in default_tools:
            self.append("tools", tool)

    def create_session(self):
        """Create a new session for this agent."""
        session = frappe.new_doc("Agent Session")
        session.agent_definition = self.name
        session.status = "active"
        session.insert()
        return session
