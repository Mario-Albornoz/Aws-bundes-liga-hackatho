from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from api.components.bets.settlement_notifier import bet_settlement_notifier
from feed_handler.cache.BetCache import bet_cache
from feed_handler.cache.dto.BetDtos import Bet, BetCreateRequest

router = APIRouter(prefix="/bets", tags=["bets"])


@router.post("/create", response_model=Bet)
async def create_bet(request: BetCreateRequest) -> Bet:
    bet = bet_cache.create_or_update_bet(request)
    await bet_settlement_notifier.push_snapshot(
        request.bet_subscription.participant.user_id
    )
    return bet


@router.websocket("/stream")
async def bet_settlement_stream(
    websocket: WebSocket,
    user_id: int = Query(
        ..., ge=1, description="User id to receive settlement messages for"
    ),
):
    await bet_settlement_notifier.subscribe(user_id, websocket)
    try:
        # send intial state of bets of which the user is part of
        current_bets = await bet_cache.get_bets_by_user_id(user_id=user_id)
        await websocket.send_json(
            {
                "type": "bet_snapshot",
                "bets": [b.model_dump(mode="json") for b in current_bets],
            }
        )
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await bet_settlement_notifier.unsubscribe(user_id, websocket)
