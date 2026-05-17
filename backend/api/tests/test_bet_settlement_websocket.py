"""WebSocket + notifier behaviour for /bets/stream."""

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from api.components.bets.router import router as bets_router
from api.components.bets.settlement_notifier import bet_settlement_notifier


@pytest.fixture(autouse=True)
def clear_notifier_connections():
    bet_settlement_notifier._connections.clear()
    yield
    bet_settlement_notifier._connections.clear()


def _mini_app_with_push() -> FastAPI:
    """Minimal app: real bets router + internal POST to trigger notify (test-only)."""

    app = FastAPI()

    @app.post("/__test_push/{user_id}")
    async def test_push(user_id: int) -> dict:
        await bet_settlement_notifier.notify_user(
            user_id,
            {"type": "bet_settled", "bet_id": "bet-test-1", "status": "SUCCESS"},
        )
        return {"ok": True}

    app.include_router(bets_router)
    return app


def test_bets_stream_accepts_connection_and_ping():
    app = FastAPI()
    app.include_router(bets_router)
    with TestClient(app) as client:
        with client.websocket_connect("/bets/stream?user_id=1") as ws:
            ws.send_text("ping")


def test_bets_stream_requires_user_id_query():
    app = FastAPI()
    app.include_router(bets_router)
    with TestClient(app) as client:
        with pytest.raises(Exception):
            with client.websocket_connect("/bets/stream"):
                pass


def test_bets_stream_receives_json_after_notify():
    app = _mini_app_with_push()
    with TestClient(app) as client:
        with client.websocket_connect("/bets/stream?user_id=7") as ws:
            r = client.post("/__test_push/7")
            assert r.status_code == 200
            msg = ws.receive_json()
            assert msg["type"] == "bet_settled"
            assert msg["bet_id"] == "bet-test-1"
            assert msg["status"] == "SUCCESS"


def test_bets_stream_notify_targets_only_subscribed_user():
    app = _mini_app_with_push()
    with TestClient(app) as client:
        with client.websocket_connect("/bets/stream?user_id=1") as ws1:
            with client.websocket_connect("/bets/stream?user_id=2") as ws2:
                client.post("/__test_push/2")
                msg = ws2.receive_json()
                assert msg["bet_id"] == "bet-test-1"
            ws1.send_text("still-connected")


def test_settlement_notifier_notify_is_noop_without_subscribers():
    import asyncio

    async def _run():
        await bet_settlement_notifier.notify_user(99, {"type": "bet_settled"})

    asyncio.run(_run())


def test_settlement_notifier_subscribe_notify_unsubscribe():
    import asyncio
    from unittest.mock import AsyncMock

    from api.components.bets.settlement_notifier import BetSettlementNotifier

    async def _run():
        notifier = BetSettlementNotifier()
        ws = AsyncMock()
        ws.send_json = AsyncMock()
        await notifier.subscribe(3, ws)
        await notifier.notify_user(3, {"type": "bet_settled", "bet_id": "x"})
        ws.send_json.assert_awaited_once_with({"type": "bet_settled", "bet_id": "x"})
        await notifier.unsubscribe(3, ws)
        await notifier.notify_user(3, {"type": "ignored"})
        assert ws.send_json.await_count == 1

    asyncio.run(_run())
