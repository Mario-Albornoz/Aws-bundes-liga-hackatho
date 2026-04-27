from fastapi import FastAPI
from contextlib import asynccontextmanager
from events.broadcaster import MatchBroadcastRegistry
from events.router import router as events_router
from positional.broadcaster import PositionalBroadcastRegistry
from positional.router import router as positional_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.match_broadcast_registry = MatchBroadcastRegistry()
    app.state.positional_broadcast_registry = PositionalBroadcastRegistry()
    yield
    await app.state.match_broadcast_registry.shutdown()
    await app.state.positional_broadcast_registry.shutdown()

app = FastAPI(lifespan=lifespan)

app.include_router(events_router)

app.include_router(positional_router)
