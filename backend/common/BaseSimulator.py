class BaseSimulator:
    """
    Replays entries from XML file as a real-time stream.

    Attributes:
        speed: Playback speed multiplier.
               1.0 = real time, 60.0 = 1 match-minute per real second.
    """

    def __init__(
        self,
        path: str,
        speed: float = 1.0,
    ):
        self.speed: float = speed
        self.path: str = path

    async def stream(self):
        """
        Async generator that yields WSMessage instances.

        Yields:
            WSMessage
        """
        raise NotImplementedError
