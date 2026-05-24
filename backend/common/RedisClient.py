import redis
import redis.asyncio
from dotenv import load_dotenv
import os

load_dotenv()

redis_client = redis.from_url(os.getenv("REDIS_URL"))
async_redis_client = redis.asyncio.from_url(os.getenv("REDIS_URL"))
