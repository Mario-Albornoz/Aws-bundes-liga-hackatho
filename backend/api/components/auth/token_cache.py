from common.RedisClient import redis_client
from api.components.auth.jwt import REFRESH_TOKEN_EXPIRE_DAYS

_TTL_SECONDS = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60


def _key(token_hash: str) -> str:
    return f"auth:refresh:{token_hash}"


def store_refresh_token(token_hash: str, user_id: int) -> None:
    redis_client.setex(_key(token_hash), _TTL_SECONDS, str(user_id))


def get_refresh_token_user_id(token_hash: str) -> int | None:
    value = redis_client.get(_key(token_hash))
    if value is None:
        return None
    return int(value)


def revoke_refresh_token(token_hash: str) -> None:
    redis_client.delete(_key(token_hash))
