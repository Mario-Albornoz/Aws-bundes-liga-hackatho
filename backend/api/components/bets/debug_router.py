"""
Debug/test endpoints for bet opportunities, bet creation, and bet status updates.
Use these to manually drive the full bet lifecycle without needing the live feed.

Opportunity endpoints
---------------------
POST /bets/debug/trigger
    Fire one fake bet_opportunity to all chat-room clients.

POST /bets/debug/loop/start?interval_seconds=5
    Start a background loop that fires one every `interval_seconds`.

POST /bets/debug/loop/stop
    Stop the background loop.

GET  /bets/debug/loop/status
    Returns whether the loop is running and the current interval.

Bet lifecycle endpoints
-----------------------
POST /bets/debug/bet/create?user_id=1&amount=10&position=true
    Create a fake PENDING bet for a user and push a snapshot update.

POST /bets/debug/bet/activate?bet_id=xxx
    Move a bet PENDING → ACTIVE and push bet_updated to participants.

POST /bets/debug/bet/settle?bet_id=xxx&won=true
    Settle a bet SUCCESS/FAILED, update balances, push bet_settled.

GET  /bets/debug/bets?user_id=1
    Return all bets for a user (reads the secondary index).
"""

import asyncio
import os
import random
import uuid
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query

from api.components.bets.settlement_notifier import bet_settlement_notifier
from api.database.DatabaseManager import database_manager
from common.RedisClient import redis_client
from feed_handler.cache.BetCache import bet_cache
from feed_handler.cache.dto.BetDtos import (
    Bet,
    BetCreateRequest,
    BetInfo,
    BetParticipant,
    BetSpecifications,
    BetStatus,
    BetSubscription,
)
from feed_handler.consumers.handlers.dto.BetTypes import BetTypes
from feed_handler.publishing_bets.BetNotifier import bet_notifier
from feed_handler.publishing_bets.BetOpportunity import BetOpportunity
from feed_handler.publishing_bets.TeamInfo import match_result_context

load_dotenv()

debug_router = APIRouter(prefix="/bets/debug", tags=["bets-debug"])

_MATCH_ID: str = os.getenv("MATCH_ID", "DFL-MAT-111111")

# ---------------------------------------------------------------------------
# Fake data pool
# ---------------------------------------------------------------------------

_FAKE_PLAYERS = [
    "T. Müller",
    "L. Goretzka",
    "J. Musiala",
    "K. Havertz",
    "F. Wirtz",
    "C. Nkunku",
    "S. Gnabry",
    "L. Nmecha",
    "K. Adeyemi",
    "B. Duda",
]

_FAKE_TEAMS = [
    "Bayern München",
    "Borussia Dortmund",
    "Bayer Leverkusen",
    "RB Leipzig",
    "Eintracht Frankfurt",
]

# The two team IDs used in the anonymised match data
_TEAM_LEFT = "DFL-CLU-000002"
_TEAM_RIGHT = "DFL-CLU-000001"


def _make_fake_opportunity(window_seconds: int = 120) -> BetOpportunity:
    player = random.choice(_FAKE_PLAYERS)
    team = random.choice(_FAKE_TEAMS)
    return BetOpportunity(
        bet_type="substitution",
        trigger_event_id=str(uuid.uuid4()),
        window_seconds=window_seconds,
        match_id=_MATCH_ID,
        context={"player_on": player, "team": team},
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=window_seconds),
        bet_id=uuid.uuid4(),
    )


# ---------------------------------------------------------------------------
# Loop state (module-level so it survives request lifecycles)
# ---------------------------------------------------------------------------

_loop_task: asyncio.Task | None = None
_loop_interval: float = 5.0


async def _broadcast_loop(interval: float) -> None:
    while True:
        opportunity = _make_fake_opportunity()
        await bet_notifier.notify(opportunity)
        await asyncio.sleep(interval)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@debug_router.post("/trigger", summary="Fire one fake bet_opportunity now")
async def trigger_once(
    window_seconds: int = Query(
        default=120,
        ge=10,
        le=600,
        description="How many seconds the betting window is open",
    ),
):
    opportunity = _make_fake_opportunity(window_seconds=window_seconds)
    await bet_notifier.notify(opportunity)
    return {
        "sent": True,
        "opportunity": opportunity.model_dump(mode="json"),
    }


@debug_router.post("/loop/start", summary="Start auto-firing loop")
async def loop_start(
    interval_seconds: float = Query(
        default=5.0,
        ge=1.0,
        le=60.0,
        description="Seconds between each fake bet_opportunity broadcast",
    ),
):
    global _loop_task, _loop_interval

    # Cancel any existing loop
    if _loop_task and not _loop_task.done():
        _loop_task.cancel()
        try:
            await _loop_task
        except asyncio.CancelledError:
            pass

    _loop_interval = interval_seconds
    _loop_task = asyncio.create_task(_broadcast_loop(_loop_interval))

    return {"running": True, "interval_seconds": _loop_interval}


@debug_router.post("/loop/stop", summary="Stop auto-firing loop")
async def loop_stop():
    global _loop_task

    if _loop_task and not _loop_task.done():
        _loop_task.cancel()
        try:
            await _loop_task
        except asyncio.CancelledError:
            pass
        _loop_task = None
        return {"running": False}

    return {"running": False, "detail": "Loop was not running"}


@debug_router.get("/loop/status", summary="Check loop status")
async def loop_status():
    running = _loop_task is not None and not _loop_task.done()
    return {
        "running": running,
        "interval_seconds": _loop_interval if running else None,
    }


# ---------------------------------------------------------------------------
# Bet lifecycle helpers
# ---------------------------------------------------------------------------


def _make_fake_bet_request(user_id: int, amount: int, position: bool) -> BetCreateRequest:
    player = random.choice(_FAKE_PLAYERS)
    team = random.choice(_FAKE_TEAMS)
    bet_id = str(uuid.uuid4())
    return BetCreateRequest(
        bet_info=BetInfo(
            bet_id=bet_id,
            bet_type=BetTypes.SUBSTITUTION,
            duration=120,
            match_id=_MATCH_ID,
            bet_specs=BetSpecifications(player_id=player, team_id=team),
        ),
        bet_subscription=BetSubscription(
            participant=BetParticipant(
                user_id=user_id,
                bet_amount=amount,
                position=position,
            )
        ),
    )


async def _push_snapshot(user_id: int) -> None:
    """Re-fetch and broadcast the user's full bet list after any state change."""
    bets = await bet_cache.get_bets_by_user_id(user_id)
    await bet_settlement_notifier.notify_user(
        user_id,
        {
            "type": "bet_snapshot",
            "bets": [b.model_dump(mode="json") for b in bets],
        },
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@debug_router.post("/bet/create", summary="Create a fake PENDING bet for a user")
async def debug_create_bet(
    user_id: int = Query(..., ge=1, description="User who places the bet"),
    amount: int = Query(default=10, ge=1, description="Stake in coins"),
    position: bool = Query(default=True, description="YES (true) or NO (false)"),
):
    request = _make_fake_bet_request(user_id, amount, position)
    bet = bet_cache.create_or_update_bet(request)
    await _push_snapshot(user_id)
    return {"created": True, "bet": bet.model_dump(mode="json")}


@debug_router.post("/bet/activate", summary="Move a bet PENDING → ACTIVE")
async def debug_activate_bet(
    bet_id: str = Query(..., description="ID of the bet to activate"),
):
    raw = redis_client.get(f"bet:{bet_id}")
    if not raw:
        raise HTTPException(status_code=404, detail=f"Bet '{bet_id}' not found")

    bet = Bet.model_validate_json(raw)
    if bet.bet_status != BetStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Bet is '{bet.bet_status.value}', only PENDING bets can be activated",
        )

    bet.triggered = True
    bet.bet_status = BetStatus.ACTIVE
    await bet_cache.update_bet(bet_id, bet)

    for participant in bet.participants:
        await bet_settlement_notifier.notify_user(
            participant.user_id,
            {
                "type": "bet_updated",
                "bet_id": bet_id,
                "status": BetStatus.ACTIVE.value,
            },
        )
        await _push_snapshot(participant.user_id)

    return {"activated": True, "bet": bet.model_dump(mode="json")}


@debug_router.post("/bet/settle", summary="Settle a bet SUCCESS or FAILED")
async def debug_settle_bet(
    bet_id: str = Query(..., description="ID of the bet to settle"),
    won: bool = Query(..., description="true = SUCCESS, false = FAILED"),
):
    raw = redis_client.get(f"bet:{bet_id}")
    if not raw:
        raise HTTPException(status_code=404, detail=f"Bet '{bet_id}' not found")

    bet = Bet.model_validate_json(raw)
    if bet.bet_status in (BetStatus.SUCCESS, BetStatus.FAILED):
        raise HTTPException(
            status_code=400,
            detail=f"Bet is already settled as '{bet.bet_status.value}'",
        )

    bet.bet_status = BetStatus.SUCCESS if won else BetStatus.FAILED
    if won:
        bet.scored = True
    await bet_cache.update_bet(bet_id, bet)

    for participant in bet.participants:
        balance = await database_manager.get_user_balance_by_id(participant.user_id) or 0.0
        if won and participant.position:
            balance += participant.bet_amount
        else:
            balance -= participant.bet_amount
        await database_manager.update_user_balance_by_id(balance, participant.user_id)

        await bet_settlement_notifier.notify_user(
            participant.user_id,
            {
                "type": "bet_settled",
                "bet_id": bet_id,
                "status": bet.bet_status.value,
                "match_id": bet.bet_info.match_id,
                "user_id": participant.user_id,
                "new_balance": balance,
            },
        )

    return {"settled": True, "bet": bet.model_dump(mode="json")}


@debug_router.get("/bets", summary="List all bets for a user")
async def debug_list_bets(
    user_id: int = Query(..., ge=1, description="User whose bets to list"),
):
    bets = await bet_cache.get_bets_by_user_id(user_id)
    return {
        "user_id": user_id,
        "count": len(bets),
        "bets": [b.model_dump(mode="json") for b in bets],
    }


# ---------------------------------------------------------------------------
# Match-result bet helpers
# ---------------------------------------------------------------------------


@debug_router.post(
    "/trigger/match_result",
    summary="Fire a fake match_result bet_opportunity to all clients",
)
async def trigger_match_result(
    window_seconds: int = Query(
        default=5400,
        ge=30,
        le=7200,
        description="Betting window in seconds (default 90 min)",
    ),
):
    opportunity = BetOpportunity(
        bet_type=BetTypes.MATCH_RESULT.value,
        trigger_event_id=str(uuid.uuid4()),
        window_seconds=window_seconds,
        match_id=_MATCH_ID,
        context=match_result_context(_TEAM_LEFT, _TEAM_RIGHT),
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=window_seconds),
        bet_id=uuid.uuid4(),
    )
    await bet_notifier.notify(opportunity)
    return {"sent": True, "opportunity": opportunity.model_dump(mode="json")}


@debug_router.post(
    "/bet/settle_match_result",
    summary="Simulate a full-time whistle and settle all match_result bets",
)
async def debug_settle_match_result(
    final_result: str = Query(
        default="1:0",
        description="Score string 'home:away' e.g. '2:1'. Home = team_left from kick-off.",
    ),
):
    """
    Parses the score and settles every open match_result bet:
    - Participants who bet on the winning team → SUCCESS
    - Everyone else (loser or draw) → FAILED
    """
    try:
        left_str, right_str = final_result.split(":")
        int(left_str)
        int(right_str)
    except ValueError:
        from fastapi import HTTPException as _HTTPException

        raise _HTTPException(
            status_code=422,
            detail="final_result must be in 'home:away' format, e.g. '2:1'",
        )

    from feed_handler.consumers.handlers.MatchResultBetHandler import (
        MatchResultBetHandler,
    )

    handler = MatchResultBetHandler()

    # Reuse the handler's internal settlement logic directly
    await handler._settle_all(final_result)

    return {"settled": True, "final_result": final_result}
