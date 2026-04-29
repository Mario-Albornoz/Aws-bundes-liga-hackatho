import pytest
from common.models import ServerMessageType
from events.EventSimulator import EventSimulator

TEST_XML = "./data/test.xml"


@pytest.mark.asyncio
async def test_stream_yields_all_events():
    sim = EventSimulator(speed=10000, path=TEST_XML)
    messages = [msg async for msg in sim.stream()]
    assert len(messages) == 10


@pytest.mark.asyncio
async def test_all_messages_have_correct_type():
    sim = EventSimulator(speed=10000, path=TEST_XML)
    async for msg in sim.stream():
        assert msg.type == ServerMessageType.EVENT
