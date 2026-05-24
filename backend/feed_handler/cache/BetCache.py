# make sure there is a singleton instace of this class across the server
from common.RedisClient import redis_client
from feed_handler.cache.dto.BetDtos import Bet, BetCreateRequest, BetStatus


class BetCache:
    @staticmethod
    def _get_participant_key(user_id: int) -> str:
        return f"user_id:{user_id}"

    @staticmethod
    def _get_bet_key(bet_id: str) -> str:
        return f"bet:{bet_id}"

    def create_or_update_bet(self, request: BetCreateRequest) -> Bet:
        bet_id = request.bet_info.bet_id
        participant = request.bet_subscription.participant
        cacheKey = self._get_bet_key(bet_id)

        cached_bet = redis_client.get(cacheKey)
        if cached_bet:
            return Bet.model_validate_json(cached_bet)

        new_bet = Bet(
            bet_info=request.bet_info,
            participants=[participant],
            bet_status=BetStatus.PENDING,
        )
        redis_client.set(cacheKey, new_bet.model_dump_json())

        redis_client.sadd(self._get_participant_key(participant.user_id), bet_id)

        return new_bet

    async def get_bets_by_type(self, bet_type: str) -> list[Bet]:
        bets = []
        cursor = 0
        while True:
            cursor, keys = redis_client.scan(cursor, match="bet:*", count=100)
            for key in keys:
                cached_bet = redis_client.get(key)
                if cached_bet:
                    bet = Bet.model_validate_json(cached_bet)
                    if bet.bet_info.bet_type == bet_type:
                        bets.append(bet)
            if cursor == 0:
                break
        return bets

    async def update_bet(self, bet_id: str, bet: Bet) -> None:
        cacheKey = self._get_bet_key(bet_id)
        redis_client.set(cacheKey, bet.model_dump_json())

    async def get_bets_by_user_id(self, user_id: int) -> list[Bet]:
        bet_ids = redis_client.smembers(self._get_participant_key(user_id))
        if not bet_ids:
            return []

        bet_keys = [self._get_bet_key(bid.decode()) for bid in bet_ids]
        raw_bets = redis_client.mget(*bet_keys)

        return [Bet.model_validate_json(raw) for raw in raw_bets if raw is not None]


bet_cache = BetCache()
