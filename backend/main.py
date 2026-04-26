from fastapi import FastAPI
from contextlib import asynccontextmanager
from events.broadcaster import BroadcastRegistry
from events.router import router as events_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.broadcast_registry = BroadcastRegistry()
    yield
    await app.state.broadcast_registry.shutdown()

app = FastAPI(lifespan=lifespan)

app.include_router(events_router)
