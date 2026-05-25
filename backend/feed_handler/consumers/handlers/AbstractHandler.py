from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class AbstractHandler(ABC, Generic[T]):
    @abstractmethod
    async def handle(self, event: T):
        pass

    @abstractmethod
    async def complete(self):
        pass
