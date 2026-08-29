"""
Adaptive Intent Classifier & NLU Router
"""
from typing import Dict, Any, List

class AdaptiveIntentClassifier:
    INTENT_KEYWORDS = {
        "QUERY_WEATHER": ["weather", "temperature", "forecast", "rain"],
        "CONTROL_DEVICE": ["turn", "switch", "lights", "thermostat", "lock"],
        "SET_REMINDER": ["remind", "alarm", "schedule", "calendar"],
        "PLAY_MEDIA": ["play", "music", "song", "podcast", "video"]
    }

    @classmethod
    def classify(cls, utterance: str) -> Dict[str, Any]:
        text = utterance.lower()
        scores = {}
        for intent, kw_list in cls.INTENT_KEYWORDS.items():
            matches = sum(1 for kw in kw_list if kw in text)
            if matches > 0:
                scores[intent] = matches / len(kw_list)

        if not scores:
            return {"intent": "FALLBACK_UNKNOWN", "confidence": 0.0, "entities": {}}

        top_intent = max(scores, key=scores.get)
        return {
            "intent": top_intent,
            "confidence": min(1.0, round(scores[top_intent] * 2, 2)),
            "entities": {"raw_input": utterance}
        }
