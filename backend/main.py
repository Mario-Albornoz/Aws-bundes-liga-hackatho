from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from feed_simulator.events.EventBroadcastRegistry import EventBroadcastRegistry
from feed_simulator.events.router import router as events_router
from feed_simulator.positional.PositionalBroadcastRegistry import (
    PositionalBroadcastRegistry,
)
from feed_simulator.positional.router import router as positional_router
from api.components.bets.router import router as bets_router
from api.components.communication.router import router as chat_room_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.match_broadcast_registry = EventBroadcastRegistry()
    app.state.positional_broadcast_registry = PositionalBroadcastRegistry()
    yield
    await app.state.match_broadcast_registry.shutdown()
    await app.state.positional_broadcast_registry.shutdown()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events_router)

app.include_router(positional_router)

app.include_router(chat_room_router)

app.include_router(bets_router)
