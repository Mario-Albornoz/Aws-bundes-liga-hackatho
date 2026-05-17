import asyncio
import json

import websockets


class EventListener:

    def __init__(
        self, uri: str = "ws://localhost:8000/events/stream?match_id=123&speed=1&seq=0"
    ) -> None:
        self.uri = uri

        asyncio.run(self.listen())

    async def listen(self):
        uri = self.uri

        async with websockets.connect(uri) as ws:
            print("Connected!")

            try:
                while True:
                    message = await ws.recv()
                    data = json.loads(message)

                    print("Received:", data)

                    if data["type"] == "MATCH_START":
                        print("Match started:", data["payload"])

                    elif data["type"] == "EVENT":
                        print("Event:", data["payload"])

            except websockets.ConnectionClosed:
                print("Connection closed")
