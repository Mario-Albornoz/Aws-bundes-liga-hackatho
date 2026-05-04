from feed_simulator.common.BaseBroadcaster import BaseBroadcaster


class BroadcastRegistry:
    """
    One broadcaster per match, shared via app.state.

    Subclasses implement:
        _broadcaster_for(match_id, path, speed) - BaseBroadcaster
    """

    def __init__(self) -> None:
        self._broadcasters: dict[str, BaseBroadcaster] = {}

    def _broadcaster_for(self, match_id: str, speed: float) -> BaseBroadcaster:
        """Construct a broadcaster instance. Override in subclasses."""
        raise NotImplementedError

    async def get_or_create(self, match_id: str, speed: float = 1.0) -> BaseBroadcaster:
        """Return existing broadcaster for a match, or create and start a new one."""
        if match_id not in self._broadcasters:
            broadcaster = self._broadcaster_for(match_id=match_id, speed=speed)
            await broadcaster.start()
            self._broadcasters[match_id] = broadcaster
        return self._broadcasters[match_id]

    async def shutdown(self) -> None:
        """Stop all active broadcasters. Called on app shutdown."""
        for broadcaster in self._broadcasters.values():
            await broadcaster.stop()
        self._broadcasters.clear()
