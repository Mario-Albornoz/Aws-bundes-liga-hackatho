from api.components.bets.settlement_notifier import bet_settlement_notifier
from api.database.DatabaseManager import database_manager
from feed_handler.cache.BetCache import bet_cache
from feed_handler.cache.dto.BetDtos import Bet, BetStatus
from feed_handler.consumers.handlers.AbstractHandler import AbstractHandler
from feed_simulator.events.models import (
    Caution,
    FinalWhistle,
    MatchEvent,
    ShotAtGoal,
    Substitution,
    SuccessfulShot,
)


class BetProcessingHandler(AbstractHandler):
    def __init__(self, bet_type: str):
        self.bet_type = bet_type

    async def complete(self) -> None:
        return None

    async def handle(self, event: MatchEvent):
        bets = await bet_cache.get_bets_by_type(self.bet_type)

        if not bets:
            return

        sub = event.subelement

        settled: list[Bet] = await self._handle_substitution_bet(sub, bets)

        for bet in settled:
            await self._settle_bet(bet)

    async def _settle_bet(self, bet: Bet) -> None:
        for participant in bet.participants:
            balance = await database_manager.get_user_balance_by_id(participant.user_id)
            if balance is None:
                balance = 0.0

            if bet.bet_status == BetStatus.SUCCESS and participant.position:
                balance += participant.bet_amount
            else:
                balance -= participant.bet_amount

            await database_manager.update_user_balance_by_id(
                balance, participant.user_id
            )
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

    async def _handle_substitution_bet(self, sub, bets) -> list:
        settled: list[Bet] = []
        if isinstance(sub, Substitution):
            for bet in bets:
                if (
                    bet.bet_status == BetStatus.PENDING
                    and sub.player_in == bet.bet_info.bet_specs.player_id
                ):
                    bet.triggered = True
                    bet.bet_status = BetStatus.ACTIVE
                    await bet_cache.update_bet(bet.bet_info.bet_id, bet)
                    print(f"Bet {bet.bet_info.bet_id} ACTIVE")
                    for participant in bet.participants:
                        await bet_settlement_notifier.notify_user(
                            participant.user_id,
                            {
                                "type": "bet_updated",
                                "bet_id": bet.bet_info.bet_id,
                                "status": bet.bet_status.value,
                            },
                        )

        elif isinstance(sub, ShotAtGoal):
            if not isinstance(sub.subelement, SuccessfulShot):
                return []

            scorer = sub.player
            for bet in bets:
                if (
                    bet.bet_status == BetStatus.ACTIVE
                    and scorer == bet.bet_info.bet_specs.player_id
                ):
                    bet.scored = True
                    bet.bet_status = BetStatus.SUCCESS
                    await bet_cache.update_bet(bet.bet_info.bet_id, bet)
                    settled.append(bet)
                    print(f"Bet {bet.bet_info.bet_id} SUCCESS")

        elif isinstance(sub, FinalWhistle):
            for bet in bets:
                # Terminal bets were already settled; do not re-run _settle_bet on
                # later FinalWhistle events (e.g. half-time vs full-time, or duplicates).
                if bet.scored and bet.bet_status not in (
                    BetStatus.SUCCESS,
                    BetStatus.FAILED,
                ):
                    bet.bet_status = BetStatus.FAILED
                    await bet_cache.update_bet(bet.bet_info.bet_id, bet)
                    settled.append(bet)
                    print(f"Bet {bet.bet_info.bet_id} FAILED")

        return settled

    async def _handle_number_of_yellow_cards(self, sub, bets) -> list:
        settled: list[Bet] = []

        if isinstance(sub, ShotAtGoal):
            for bet in bets:
                if bet.bet_status == BetStatus.PENDING:
                    bet.triggered = True
                    bet.bet_status = BetStatus.ACTIVE
                    await bet_cache.update_bet(bet.bet_info.bet_id, bet)
                    for participant in bet.participants:
                        await bet_settlement_notifier.notify_user(
                            participant.user_id,
                            {
                                "type": "bet_updated",
                                "bet_id": bet.bet_info.bet_id,
                                "status": bet.bet_status.value,
                            },
                        )

        return settled
