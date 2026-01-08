# Copyright (c) 2025, Frappe Accelerated and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DeepAgentSettings(Document):
    def validate(self):
        if self.default_llm_provider == "OpenRouter" and not self.openrouter_api_key:
            frappe.throw("OpenRouter API Key is required when using OpenRouter provider")

        if self.sandbox_timeout_minutes and self.sandbox_timeout_minutes < 1:
            frappe.throw("Sandbox timeout must be at least 1 minute")

    def test_llm_connection(self):
        """Test connection to the configured LLM provider."""
        from frappe_deep_agents.services.llm_service import LLMService

        service = LLMService()
        return service.test_connection()
