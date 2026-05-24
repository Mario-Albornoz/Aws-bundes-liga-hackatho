"""
Handles the full lifecycle of MATCH_RESULT bets.

Lifecycle
---------
PENDING  → user places bet after KickOff opportunity is published
ACTIVE   → automatically on secondHalf KickOff (match resumes)
SUCCESS  → on secondHalf FinalWhistle, if the user's chosen team won
FAILED   → on secondHalf FinalWhistle, if the user's chosen team lost or drew
"""

from api.components.bets.settlement_notifier import bet_settlement_notifier
from api.database.DatabaseManager import database_manager
from feed_handler.cache.BetCache import bet_cache
from feed_handler.cache.dto.BetDtos import Bet, BetStatus
from feed_handler.consumers.handlers.AbstractHandler import AbstractHandler
from feed_handler.consumers.handlers.dto.BetTypes import BetTypes
from feed_simulator.events.models import FinalWhistle, KickOff, MatchEvent


class MatchResultBetHandler(AbstractHandler):
    def __init__(self) -> None:
        self.bet_type = BetTypes.MATCH_RESULT.value

    async def complete(self) -> None:
        return None

    async def handle(self, event: MatchEvent) -> None:
        sub = event.subelement

        if isinstance(sub, KickOff) and sub.game_section == "secondHalf":
            await self._activate_pending_bets()
            return

        if isinstance(sub, FinalWhistle) and sub.game_section == "secondHalf":
            await self._settle_all(sub.final_result)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _activate_pending_bets(self) -> None:
        bets = await bet_cache.get_bets_by_type(self.bet_type)
        for bet in bets:
            if bet.bet_status != BetStatus.PENDING:
                continue
            bet.bet_status = BetStatus.ACTIVE
            bet.triggered = True
            await bet_cache.update_bet(bet.bet_info.bet_id, bet)
            print(f"Match-result bet {bet.bet_info.bet_id} → ACTIVE")
            for participant in bet.participants:
                await bet_settlement_notifier.notify_user(
                    participant.user_id,
                    {
                        "type": "bet_updated",
                        "bet_id": bet.bet_info.bet_id,
                        "status": BetStatus.ACTIVE.value,
                    },
                )

    async def _settle_all(self, final_result: str) -> None:
        bets = await bet_cache.get_bets_by_type(self.bet_type)
        if not bets:
            return

        try:
            left_str, right_str = final_result.split(":")
            left_goals = int(left_str)
            right_goals = int(right_str)
        except (ValueError, AttributeError):
            print(f"MatchResultBetHandler: cannot parse final_result '{final_result}'")
            return

        for bet in bets:
            if bet.bet_status in (BetStatus.SUCCESS, BetStatus.FAILED):
                continue

            team_left = bet.bet_info.bet_specs.team_left
            team_right = bet.bet_info.bet_specs.team_right
            chosen_team = bet.bet_info.bet_specs.team_id

            if not team_left or not team_right or not chosen_team:
                continue

            if left_goals > right_goals:
                winning_team = team_left
            elif right_goals > left_goals:
                winning_team = team_right
            else:
                winning_team = None  # draw

            # position=True always means "I bet my chosen team wins"
            user_team_won = winning_team is not None and winning_team == chosen_team

            bet.bet_status = BetStatus.SUCCESS if user_team_won else BetStatus.FAILED
            bet.triggered = True
            await bet_cache.update_bet(bet.bet_info.bet_id, bet)
            print(f"Match-result bet {bet.bet_info.bet_id} → {bet.bet_status.value}")

            await self._settle_participant_balances(bet)

    async def _settle_participant_balances(self, bet: Bet) -> None:
        for participant in bet.participants:
            balance = await database_manager.get_user_balance_by_id(participant.user_id)
            if balance is None:
                balance = 0.0

            if bet.bet_status == BetStatus.SUCCESS and participant.position:
                balance += participant.bet_amount
            else:
                balance -= participant.bet_amount

            await database_manager.update_user_balance_by_id(balance, participant.user_id)
            await bet_settlement_notifier.notify_user(
                participant.user_id,
                {
                    "type": "bet_settled",
                    "bet_id": bet.bet_info.bet_id,
                    "status": bet.bet_status.value,
                    "match_id": bet.bet_info.match_id,
                    "user_id": participant.user_id,
                    "new_balance": balance,
                },
            )
