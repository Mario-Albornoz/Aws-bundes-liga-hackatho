from pathlib import Path
 
import pytest
from common.models import ServerMessageType
from events.simulator import EventSimulator
 
SAMPLE_XML = Path("data/events_sample.xml")
 
 
@pytest.mark.asyncio
async def test_stream_yields_all_events():
    sim = EventSimulator(speed=10000)
    messages = [msg async for msg in sim.stream()]
    assert len(messages) == 10

@pytest.mark.asyncio
async def test_all_messages_have_correct_type():
    sim = EventSimulator(speed=10000)
    async for msg in sim.stream():
        assert msg.type == ServerMessageType.EVENT