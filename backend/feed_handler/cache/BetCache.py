# make sure there is a singleton instace of this class across the server
from feed_handler.cache.dto.BetDtos import Bet, BetCreateRequest, BetStatus


class BetCache:
    def __init__(self) -> None:
        self._bets: dict[str, Bet] = {}

    def create_or_update_bet(self, request: BetCreateRequest) -> Bet:
        bet_id = request.bet_info.bet_id
        participant = request.bet_subscription.participant

        if bet_id in self._bets:
            self._bets[bet_id].participants.append(participant)
            return self._bets[bet_id]

        new_bet = Bet(
            bet_info=request.bet_info,
            participants=[participant],
            bet_status=BetStatus.PENDING,
        )

        self._bets[bet_id] = new_bet
        return new_bet

    async def get_bets_by_type(self, bet_type: str):
        return [bet for bet in self._bets.values() if bet.bet_info.bet_type == bet_type]

    async def update_bet(self, bet_id: str, bet: Bet):
        self._bets[bet_id] = bet


bet_cache = BetCache()
