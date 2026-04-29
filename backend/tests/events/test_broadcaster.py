import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from events.EventBroadcaster import EventBroadcaster
from events.EventBroadcastRegistry import EventBroadcastRegistry


def mock_websocket():
    ws = MagicMock()
    ws.send_text = AsyncMock()
    return ws


@pytest.mark.asyncio
async def test_all_clients_receive_same_messages():
    broadcaster = EventBroadcaster(match_id="test", speed=10_000)
    await broadcaster.start()

    ws1 = mock_websocket()
    ws2 = mock_websocket()

    await broadcaster.connect("client-1", ws1, resume_seq=0)
    await broadcaster.connect("client-2", ws2, resume_seq=0)

    await asyncio.sleep(0.5)

    calls1 = [call.args[0] for call in ws1.send_text.call_args_list]
    calls2 = [call.args[0] for call in ws2.send_text.call_args_list]

    assert calls1 == calls2


@pytest.mark.asyncio
async def test_catchup_sends_missed_messages():
    broadcaster = EventBroadcaster(match_id="test", speed=10_000)
    await broadcaster.start()

    await asyncio.sleep(0.3)

    ws = mock_websocket()
    await broadcaster.connect("late-client", ws, resume_seq=0)

    assert ws.send_text.call_count > 0


@pytest.mark.asyncio
async def test_catchup_respects_resume_seq():
    broadcaster = EventBroadcaster(match_id="test", speed=10_000)
    await broadcaster.start()

    await asyncio.sleep(0.5)

    ws = mock_websocket()

    await broadcaster.connect("resuming-client", ws, resume_seq=5)

    sent = [call.args[0] for call in ws.send_text.call_args_list]
    import json

    seqs = [json.loads(msg)["seq"] for msg in sent if json.loads(msg).get("seq", 0) > 0]
    assert all(s > 5 for s in seqs)


@pytest.mark.asyncio
async def test_disconnect_removes_client():
    broadcaster = EventBroadcaster(match_id="test", speed=10_000)
    await broadcaster.start()

    ws = mock_websocket()
    await broadcaster.connect("client-1", ws, resume_seq=0)
    assert broadcaster.client_count == 1

    await broadcaster.disconnect("client-1")
    assert broadcaster.client_count == 0


@pytest.mark.asyncio
async def test_registry_reuses_broadcaster_for_same_match():
    registry = EventBroadcastRegistry()

    b1 = await registry.get_or_create("DFL-MAT-0025K6")
    b2 = await registry.get_or_create("DFL-MAT-0025K6")

    assert b1 is b2

    await registry.shutdown()


@pytest.mark.asyncio
async def test_registry_creates_separate_broadcasters_per_match():
    registry = EventBroadcastRegistry()

    b1 = await registry.get_or_create("match-1")
    b2 = await registry.get_or_create("match-2")

    assert b1 is not b2

    await registry.shutdown()
