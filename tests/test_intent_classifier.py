from sih.nlu.intent_classifier import AdaptiveIntentClassifier

def test_intent_classification():
    res = AdaptiveIntentClassifier.classify("Turn on the living room lights")
    assert res["intent"] == "CONTROL_DEVICE"
    assert res["confidence"] > 0.0

def test_fallback_intent():
    res = AdaptiveIntentClassifier.classify("xyzabc unknown gibberish")
    assert res["intent"] == "FALLBACK_UNKNOWN"
