# make sure there is a singleton instace of this class across the server
from feed_handler.cache.dto.BetDtos import Bet, BetCreateRequest, BetStatus
from common.RedisClient import redis_client


class BetCache:
    def create_or_update_bet(self, request: BetCreateRequest) -> Bet:
        bet_id = request.bet_info.bet_id
        participant = request.bet_subscription.participant
        cacheKey = f"bet:{bet_id}"

        cached_bet = redis_client.get(cacheKey)
        if cached_bet:
            return Bet.model_validate_json(cached_bet)

        new_bet = Bet(
            bet_info=request.bet_info,
            participants=[participant],
            bet_status=BetStatus.PENDING,
        )
        redis_client.set(cacheKey, new_bet.model_dump_json())

        return new_bet

    async def get_bets_by_type(self, bet_type: str):
        keys = redis_client.keys("bet:*")
        bets = []
        for key in keys:
            cached_bet = redis_client.get(key)
            if cached_bet:
                bet = Bet.model_validate_json(cached_bet)
                if bet.bet_info.bet_type == bet_type:
                    bets.append(bet)
        return bets

    async def update_bet(self, bet_id: str, bet: Bet):
        cacheKey = f"bet:{bet_id}"
        redis_client.delete(cacheKey)
        redis_client.set(cacheKey, bet.model_dump_json())


bet_cache = BetCache()
