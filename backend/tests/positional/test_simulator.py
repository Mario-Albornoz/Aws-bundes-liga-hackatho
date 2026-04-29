import pytest
from common.models import ServerMessageType
from positional.PositionalSimulator import PositionalSimulator

TEST_XML = "./data/test_positional.xml"


@pytest.mark.asyncio
async def test_stream_yields_all_frames():
    sim = PositionalSimulator(speed=10000, path=TEST_XML)
    messages = [msg async for msg in sim.stream()]
    assert len(messages) == 7


@pytest.mark.asyncio
async def test_all_messages_have_correct_type():
    sim = PositionalSimulator(speed=10000, path=TEST_XML)
    async for msg in sim.stream():
        assert msg.type == ServerMessageType.POSITIONAL


@pytest.mark.asyncio
async def test_payload_has_players():
    sim = PositionalSimulator(speed=10000, path=TEST_XML)
    async for msg in sim.stream():
        assert len(msg.payload.players) == 2


@pytest.mark.asyncio
async def test_payload_has_ball():
    sim = PositionalSimulator(speed=10000, path=TEST_XML)
    async for msg in sim.stream():
        assert msg.payload.ball is not None


@pytest.mark.asyncio
async def test_stream_called_twice_yields_same_results():
    sim = PositionalSimulator(speed=10000, path=TEST_XML)
    first = [msg.seq async for msg in sim.stream()]
    second = [msg.seq async for msg in sim.stream()]
    assert first == second
