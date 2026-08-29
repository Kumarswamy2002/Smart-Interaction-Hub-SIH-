from sih.core.context_fusion import MultimodalContextFusionEngine

def test_context_fusion_ingestion():
    engine = MultimodalContextFusionEngine()
    engine.ingest_event("s1", "voice", {"transcript": "Turn on lights"})
    engine.ingest_event("s1", "vision", {"object": "living_room"})
    fused = engine.fuse_context("s1")
    assert fused["active_event_count"] == 2
    assert "voice" in fused["modalities_present"]
    assert "vision" in fused["modalities_present"]
