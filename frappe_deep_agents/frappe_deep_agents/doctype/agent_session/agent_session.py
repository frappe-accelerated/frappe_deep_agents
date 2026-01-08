# Copyright (c) 2025, Frappe Accelerated and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class AgentSession(Document):
    def before_insert(self):
        self.started_at = now_datetime()

    def on_trash(self):
        # Cleanup sandbox on delete
        if self.sandbox_pod:
            try:
                from frappe_deep_agents.services.sandbox_service import SandboxService
                sandbox = SandboxService()
                sandbox.cleanup_sandbox(self.name)
            except Exception as e:
                frappe.log_error(
                    title=f"Sandbox cleanup failed: {self.name}",
                    message=str(e)
                )

        # Delete related todos
        frappe.db.delete("Agent Todo", {"session": self.name})

        # Delete related files
        frappe.db.delete("Agent File", {"session": self.name})

    def get_messages_for_llm(self):
        """Get messages formatted for LLM input."""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.messages
            if msg.role in ["user", "assistant", "system"]
        ]
