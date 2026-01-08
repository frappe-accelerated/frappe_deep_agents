"""
LLM Service for unified access to OpenRouter and Ollama.
"""
import frappe
from typing import Optional, AsyncIterator


class LLMService:
    """
    Unified LLM interface for OpenRouter and Ollama.

    Provides consistent API for both providers with streaming support.
    """

    def __init__(self, provider: str = None, model: str = None):
        """
        Initialize LLM service.

        Args:
            provider: LLM provider ("OpenRouter" or "Ollama"), defaults to settings
            model: Model name, defaults to settings
        """
        self.settings = frappe.get_single("Deep Agent Settings")
        self.provider = provider or self.settings.default_llm_provider
        self.model = model or self._get_default_model()

    def _get_default_model(self) -> str:
        """Get default model based on provider."""
        if self.provider == "OpenRouter":
            return self.settings.openrouter_model or "anthropic/claude-sonnet-4"
        else:
            return self.settings.ollama_model or "llama3.1"

    def get_langchain_llm(self):
        """
        Return LangChain-compatible LLM instance.

        Returns:
            BaseChatModel instance for use with LangChain/LangGraph
        """
        if self.provider == "OpenRouter":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.settings.get_password("openrouter_api_key"),
                model=self.model,
                streaming=True
            )
        else:  # Ollama
            from langchain_ollama import ChatOllama

            return ChatOllama(
                base_url=self.settings.ollama_url or "http://localhost:11434",
                model=self.model
            )

    async def stream_response(
        self,
        messages: list,
        callback=None
    ) -> AsyncIterator[str]:
        """
        Stream LLM response.

        Args:
            messages: List of message dicts with role and content
            callback: Optional callback for each token

        Yields:
            Token strings as they arrive
        """
        llm = self.get_langchain_llm()

        # Convert to LangChain message format
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

        lc_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
            else:
                lc_messages.append(HumanMessage(content=content))

        # Stream response
        async for chunk in llm.astream(lc_messages):
            token = chunk.content
            if callback:
                await callback(token)
            yield token

    def complete(self, messages: list) -> str:
        """
        Synchronous completion (non-streaming).

        Args:
            messages: List of message dicts

        Returns:
            Complete response string
        """
        llm = self.get_langchain_llm()

        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

        lc_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
            else:
                lc_messages.append(HumanMessage(content=content))

        response = llm.invoke(lc_messages)
        return response.content

    def test_connection(self) -> dict:
        """
        Test connection to the LLM provider.

        Returns:
            dict with success status and message
        """
        try:
            response = self.complete([
                {"role": "user", "content": "Say 'connection successful' in exactly those words."}
            ])

            if response and "successful" in response.lower():
                return {
                    "success": True,
                    "message": f"{self.provider} ({self.model}) is working.",
                    "response": response
                }
            return {
                "success": True,
                "message": f"{self.provider} ({self.model}) responded.",
                "response": response
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}"
            }


def get_llm_service(
    provider: str = None,
    model: str = None
) -> LLMService:
    """
    Factory function to get LLM service.

    Args:
        provider: Optional provider override
        model: Optional model override

    Returns:
        Configured LLMService instance
    """
    return LLMService(provider=provider, model=model)
