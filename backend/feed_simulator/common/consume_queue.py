import asyncio
from fastapi import WebSocket


async def consume_queue(queue: asyncio.Queue, websocket: WebSocket) -> None:
    try:
        while True:
            message = await queue.get()
            await websocket.send_text(message)
    except asyncio.CancelledError:
        pass
    except Exception:
        pass
