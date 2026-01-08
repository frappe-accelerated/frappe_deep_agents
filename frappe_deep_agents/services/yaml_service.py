"""
YAML Service for agent definition export/import.
"""
import frappe
import yaml
import json
from typing import Optional


class YAMLService:
    """
    Export and import agent definitions as YAML.

    Enables version control and sharing of agent configurations.
    """

    @staticmethod
    def export_agent(agent_name: str) -> str:
        """
        Export agent definition to YAML.

        Args:
            agent_name: Agent Definition name

        Returns:
            YAML string representation
        """
        agent = frappe.get_doc("Agent Definition", agent_name)

        config = {
            "name": agent.agent_name,
            "description": agent.description or "",
            "system_prompt": agent.system_prompt or "",
            "llm": {
                "provider": agent.llm_provider or "Default",
                "model": agent.llm_model or ""
            },
            "features": {
                "subagents": bool(agent.enable_subagents),
                "filesystem": bool(agent.enable_filesystem),
                "todos": bool(agent.enable_todos)
            },
            "tools": []
        }

        # Export tools
        for tool in agent.tools:
            tool_config = {
                "name": tool.tool_name,
                "type": tool.tool_type or "builtin",
                "enabled": bool(tool.enabled)
            }

            # Parse config JSON if present
            if tool.config_json:
                try:
                    tool_config["config"] = json.loads(tool.config_json)
                except json.JSONDecodeError:
                    pass

            config["tools"].append(tool_config)

        return yaml.dump(config, default_flow_style=False, allow_unicode=True)

    @staticmethod
    def import_agent(yaml_content: str) -> str:
        """
        Import agent definition from YAML.

        Creates new agent or updates existing one with same name.

        Args:
            yaml_content: YAML string

        Returns:
            Agent Definition name
        """
        config = yaml.safe_load(yaml_content)

        if not config.get("name"):
            frappe.throw("Agent name is required in YAML")

        agent_name = config["name"]

        # Check if agent exists
        existing = frappe.db.exists("Agent Definition", {"agent_name": agent_name})

        if existing:
            agent = frappe.get_doc("Agent Definition", existing)
        else:
            agent = frappe.new_doc("Agent Definition")
            agent.agent_name = agent_name

        # Update fields
        agent.description = config.get("description", "")
        agent.system_prompt = config.get("system_prompt", "")

        # LLM settings
        llm_config = config.get("llm", {})
        agent.llm_provider = llm_config.get("provider", "Default")
        agent.llm_model = llm_config.get("model", "")

        # Features
        features = config.get("features", {})
        agent.enable_subagents = features.get("subagents", False)
        agent.enable_filesystem = features.get("filesystem", True)
        agent.enable_todos = features.get("todos", True)

        # Clear and rebuild tools
        agent.tools = []
        for tool_config in config.get("tools", []):
            agent.append("tools", {
                "tool_name": tool_config.get("name"),
                "tool_type": tool_config.get("type", "builtin"),
                "enabled": tool_config.get("enabled", True),
                "config_json": json.dumps(tool_config.get("config", {}))
            })

        # Store original YAML
        agent.yaml_config = yaml_content

        agent.save()
        frappe.db.commit()

        return agent.name

    @staticmethod
    def validate_yaml(yaml_content: str) -> dict:
        """
        Validate YAML configuration.

        Args:
            yaml_content: YAML string to validate

        Returns:
            dict with valid status and any errors
        """
        errors = []

        try:
            config = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            return {
                "valid": False,
                "errors": [f"Invalid YAML: {str(e)}"]
            }

        if not isinstance(config, dict):
            return {
                "valid": False,
                "errors": ["YAML must be a dictionary"]
            }

        # Required fields
        if not config.get("name"):
            errors.append("Missing required field: name")

        # Validate LLM config
        llm = config.get("llm", {})
        if llm.get("provider") and llm["provider"] not in ["Default", "OpenRouter", "Ollama"]:
            errors.append(f"Invalid LLM provider: {llm['provider']}")

        # Validate tools
        for i, tool in enumerate(config.get("tools", [])):
            if not tool.get("name"):
                errors.append(f"Tool {i+1} missing name")
            if tool.get("type") and tool["type"] not in ["builtin", "mcp", "custom"]:
                errors.append(f"Tool {i+1} has invalid type: {tool['type']}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "config": config if len(errors) == 0 else None
        }

    @staticmethod
    def get_template() -> str:
        """
        Get a template YAML for new agents.

        Returns:
            Template YAML string
        """
        template = {
            "name": "my-agent",
            "description": "A helpful assistant",
            "system_prompt": "You are a helpful assistant. Be concise and accurate.",
            "llm": {
                "provider": "Default",
                "model": ""
            },
            "features": {
                "subagents": False,
                "filesystem": True,
                "todos": True
            },
            "tools": [
                {"name": "read_file", "type": "builtin", "enabled": True},
                {"name": "write_file", "type": "builtin", "enabled": True},
                {"name": "glob", "type": "builtin", "enabled": True},
                {"name": "grep", "type": "builtin", "enabled": True},
                {"name": "bash", "type": "builtin", "enabled": True},
                {"name": "write_todos", "type": "builtin", "enabled": True}
            ]
        }

        return yaml.dump(template, default_flow_style=False, allow_unicode=True)
