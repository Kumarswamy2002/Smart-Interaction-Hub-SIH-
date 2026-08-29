import pytest
from sih.core.event_stream import StreamEventBus

@pytest.mark.asyncio
async def test_event_bus_delivery():
    bus = StreamEventBus()
    received = []
    bus.subscribe("iot.sensors", lambda msg: received.append(msg))
    await bus.publish("iot.sensors", {"temp": 24.5})
    assert len(received) == 1
    assert received[0]["temp"] == 24.5
