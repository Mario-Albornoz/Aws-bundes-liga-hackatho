from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from api.components.bets.settlement_notifier import bet_settlement_notifier
from feed_handler.cache.BetCache import bet_cache
from feed_handler.cache.dto.BetDtos import Bet, BetCreateRequest

router = APIRouter(prefix="/bets", tags=["bets"])


@router.post("/create", response_model=Bet)
async def create_bet(request: BetCreateRequest) -> Bet:
    return bet_cache.create_or_update_bet(request)


@router.websocket("/stream")
async def bet_settlement_stream(
    websocket: WebSocket,
    user_id: int = Query(..., ge=1, description="User id to receive settlement messages for"),
):
    await bet_settlement_notifier.subscribe(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await bet_settlement_notifier.unsubscribe(user_id, websocket)
