import json
from typing import Any
from sih.domain.intent.models import Intent, IntentType
from sih.domain.intelligence.llm_adapter import get_llm_provider, BaseLLMProvider

class IntelligenceService:
    def __init__(self, provider: BaseLLMProvider | None = None):
        self.provider = provider or get_llm_provider()

    async def extract_intent(self, prompt: str, context_summary: str | None = None) -> Intent:
        system_prompt = (
            "You are the SIH Intent Parsing Engine. Convert natural language into structured intent.\n"
            "Respond strictly in JSON format with fields: intent_type, target, deadline, required_capabilities, parameters.\n"
            f"Context: {context_summary or 'None'}"
        )
        llm_response = await self.provider.generate_completion(prompt, system_prompt)
        
        try:
            parsed = json.loads(llm_response)
            intent_type_str = parsed.get("intent_type", "GENERIC_QUERY")
            try:
                intent_type = IntentType(intent_type_str)
            except ValueError:
                intent_type = IntentType.GENERIC_QUERY

            return Intent(
                type=intent_type,
                raw_prompt=prompt,
                target=parsed.get("target", "System"),
                deadline=parsed.get("deadline"),
                required_capabilities=parsed.get("required_capabilities", []),
                parameters=parsed.get("parameters", {}),
                confidence=0.95
            )
        except Exception:
            return Intent(
                type=IntentType.GENERIC_QUERY,
                raw_prompt=prompt,
                target="System",
                required_capabilities=["query"],
                confidence=0.5
            )

intelligence_service = IntelligenceService()
