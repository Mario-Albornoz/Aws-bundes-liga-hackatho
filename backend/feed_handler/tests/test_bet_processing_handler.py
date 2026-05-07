"""BetProcessingHandler settlement and idempotence (mocked DB + notifier + cache)."""

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from feed_handler.cache.dto.BetDtos import (
    Bet,
    BetInfo,
    BetParticipant,
    BetSpecifications,
    BetStatus,
)
from feed_handler.consumers.handlers.BetProcessingHandler import BetProcessingHandler
from feed_handler.consumers.handlers.dto.BetTypes import BetTypes
from feed_simulator.events.models import (
    FinalWhistle,
    MatchEvent,
    OtherShot,
    ShotAtGoal,
    SuccessfulShot,
)


def _make_bet(
    *,
    bet_id: str = "bet-1",
    player_id: str = "striker-9",
    status: BetStatus = BetStatus.ACTIVE,
    scored: bool = False,
    user_id: int = 1,
    bet_amount: int = 10,
    position: bool = True,
) -> Bet:
    return Bet(
        bet_info=BetInfo(
            bet_id=bet_id,
            bet_type=BetTypes.SUBSTITUTION,
            duration=90,
            match_id=42,
            bet_specs=BetSpecifications(player_id=player_id),
        ),
        participants=[
            BetParticipant(user_id=user_id, bet_amount=bet_amount, position=position)
        ],
        bet_status=status,
        scored=scored,
    )


def _wrap_match(sub) -> MatchEvent:
    return MatchEvent.model_construct(
        event_id="e1",
        match_id="m1",
        event_time=datetime.now(timezone.utc),
        event_type="ShotAtGoal",
        subelement=sub,
    )


def _successful_goal_shot(scorer: str) -> ShotAtGoal:
    inner = SuccessfulShot.model_construct(
        solo=True,
        goal_zone=1,
        current_result="1-0",
    )
    return ShotAtGoal.model_construct(player=scorer, subelement=inner)


def test_successful_goal_settles_active_matching_player_bet():
    bet = _make_bet()
    shot = _successful_goal_shot("striker-9")
    event = _wrap_match(shot)

    mock_get = AsyncMock(return_value=100.0)
    mock_update = AsyncMock()
    mock_notify = AsyncMock()
    mock_cache_update = AsyncMock()

    async def _run():
        with (
            patch(
                "feed_handler.consumers.handlers.BetProcessingHandler.database_manager"
            ) as db,
            patch(
                "feed_handler.consumers.handlers.BetProcessingHandler.bet_settlement_notifier"
            ) as notifier,
            patch(
                "feed_handler.consumers.handlers.BetProcessingHandler.bet_cache"
            ) as cache,
        ):
            db.get_user_balance_by_id = mock_get
            db.update_user_balance_by_id = mock_update
            notifier.notify_user = mock_notify
            cache.get_bets_by_type = AsyncMock(return_value=[bet])
            cache.update_bet = mock_cache_update

            h = BetProcessingHandler(BetTypes.SUBSTITUTION.value)
            await h.handle(event)

        assert bet.bet_status == BetStatus.SUCCESS
        assert bet.scored is True
        mock_cache_update.assert_awaited()
        mock_update.assert_awaited_once_with(110.0, 1)
        mock_notify.assert_awaited()
        args, _ = mock_notify.call_args
        assert args[0] == 1
        assert args[1]["type"] == "bet_settled"
        assert args[1]["status"] == "SUCCESS"
        assert args[1]["new_balance"] == 110.0

    asyncio.run(_run())


def test_goal_miss_non_successful_shot_returns_without_settlement():
    bet = _make_bet()
    shot = ShotAtGoal.model_construct(player="striker-9", subelement=OtherShot())
    event = _wrap_match(shot)

    mock_update = AsyncMock()
    mock_notify = AsyncMock()

    async def _run():
        with (
            patch(
                "feed_handler.consumers.handlers.BetProcessingHandler.database_manager"
            ) as db,
            patch(
                "feed_handler.consumers.handlers.BetProcessingHandler.bet_settlement_notifier"
            ) as notifier,
            patch(
                "feed_handler.consumers.handlers.BetProcessingHandler.bet_cache"
            ) as cache,
        ):
            db.update_user_balance_by_id = mock_update
            notifier.notify_user = mock_notify
            cache.get_bets_by_type = AsyncMock(return_value=[bet])
            cache.update_bet = AsyncMock()

            h = BetProcessingHandler(BetTypes.SUBSTITUTION.value)
            await h.handle(event)

        mock_update.assert_not_awaited()
        mock_notify.assert_not_awaited()

    asyncio.run(_run())


def test_final_whistle_failed_bet_settled_once_on_repeated_whistle():
    bet = _make_bet(status=BetStatus.PENDING, scored=True)
    fw = FinalWhistle.model_construct(
        game_section="FT",
        final_result="1-0",
        breaking_off=False,
    )
    event = MatchEvent.model_construct(
        event_id="e2",
        match_id="m1",
        event_time=datetime.now(timezone.utc),
        event_type="FinalWhistle",
        subelement=fw,
    )

    mock_get = AsyncMock(return_value=50.0)
    mock_update = AsyncMock()
    mock_notify = AsyncMock()

    async def _run():
        with (
            patch(
                "feed_handler.consumers.handlers.BetProcessingHandler.database_manager"
            ) as db,
            patch(
                "feed_handler.consumers.handlers.BetProcessingHandler.bet_settlement_notifier"
            ) as notifier,
            patch(
                "feed_handler.consumers.handlers.BetProcessingHandler.bet_cache"
            ) as cache,
        ):
            db.get_user_balance_by_id = mock_get
            db.update_user_balance_by_id = mock_update
            notifier.notify_user = mock_notify
            cache.get_bets_by_type = AsyncMock(return_value=[bet])
            cache.update_bet = AsyncMock()

            h = BetProcessingHandler(BetTypes.SUBSTITUTION.value)
            await h.handle(event)
            assert bet.bet_status == BetStatus.FAILED
            await h.handle(event)

        assert mock_update.await_count == 1
        assert mock_notify.await_count == 1

    asyncio.run(_run())


def test_wrong_scorer_does_not_settle():
    bet = _make_bet(player_id="striker-9")
    shot = _successful_goal_shot("other-player")
    event = _wrap_match(shot)

    mock_update = AsyncMock()

    async def _run():
        with (
            patch(
                "feed_handler.consumers.handlers.BetProcessingHandler.database_manager"
            ) as db,
            patch(
                "feed_handler.consumers.handlers.BetProcessingHandler.bet_settlement_notifier"
            ) as notifier,
            patch(
                "feed_handler.consumers.handlers.BetProcessingHandler.bet_cache"
            ) as cache,
        ):
            db.update_user_balance_by_id = mock_update
            notifier.notify_user = AsyncMock()
            cache.get_bets_by_type = AsyncMock(return_value=[bet])
            cache.update_bet = AsyncMock()
            h = BetProcessingHandler(BetTypes.SUBSTITUTION.value)
            await h.handle(event)

        mock_update.assert_not_awaited()

    asyncio.run(_run())
