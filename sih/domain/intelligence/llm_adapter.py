from abc import ABC, abstractmethod
from typing import Any
import httpx
from sih.core.config import settings

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_completion(self, prompt: str, system_prompt: str | None = None) -> str:
        pass

class MockLLMProvider(BaseLLMProvider):
    """Deterministic, high-performance mock provider for offline & fast execution."""
    async def generate_completion(self, prompt: str, system_prompt: str | None = None) -> str:
        prompt_lower = prompt.lower()
        if "meeting" in prompt_lower or "prepare" in prompt_lower:
            return '{"intent_type": "PREPARE_MEETING", "target": "Tomorrow Project Meeting", "deadline": "tomorrow", "required_capabilities": ["find_meeting", "find_participants", "find_documents", "find_tasks"]}'
        elif "task" in prompt_lower:
            return '{"intent_type": "CREATE_TASK", "target": "Task", "deadline": "today", "required_capabilities": ["create_task"]}'
        elif "workflow" in prompt_lower:
            return '{"intent_type": "EXECUTE_WORKFLOW", "target": "Workflow", "required_capabilities": ["start_workflow"]}'
        elif "message" in prompt_lower or "email" in prompt_lower:
            return '{"intent_type": "SEND_MESSAGE", "target": "Email/Messaging", "required_capabilities": ["send_email"]}'
        else:
            return f'{{"intent_type": "GENERIC_QUERY", "target": "System", "required_capabilities": ["query"]}}'

class OpenAILLMProvider(BaseLLMProvider):
    async def generate_completion(self, prompt: str, system_prompt: str | None = None) -> str:
        if not settings.OPENAI_API_KEY:
            return await MockLLMProvider().generate_completion(prompt, system_prompt)
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt or "You are SIH Intelligence Engine."},
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=30.0
            )
            data = resp.json()
            return data["choices"][0]["message"]["content"]

class OllamaLLMProvider(BaseLLMProvider):
    async def generate_completion(self, prompt: str, system_prompt: str | None = None) -> str:
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{settings.OLLAMA_BASE_URL}/api/generate",
                    json={"model": "llama3", "prompt": f"{system_prompt}\n\n{prompt}", "stream": False},
                    timeout=30.0
                )
                return resp.json().get("response", "")
            except Exception:
                return await MockLLMProvider().generate_completion(prompt, system_prompt)

def get_llm_provider(provider_name: str | None = None) -> BaseLLMProvider:
    name = provider_name or settings.DEFAULT_LLM_PROVIDER
    if name == "openai":
        return OpenAILLMProvider()
    elif name == "ollama":
        return OllamaLLMProvider()
    return MockLLMProvider()
