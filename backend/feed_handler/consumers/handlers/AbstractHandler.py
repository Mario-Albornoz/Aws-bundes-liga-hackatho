from abc import ABC, abstractclassmethod, abstractmethod

from feed_simulator.events.models import MatchEvent


class AbstractHandler(ABC):
    @abstractmethod
    async def handle(self, event: MatchEvent):
        pass

    @abstractmethod
    async def complete(self):
        pass
