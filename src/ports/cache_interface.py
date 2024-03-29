from abc import ABC, abstractmethod


class CacheInterface(ABC):

    silent_mode: bool

    def __init__(self, silent_mode: bool):
        self.silent_mode = silent_mode

    @abstractmethod
    async def get(self, key: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    async def set(self, key: str, data: dict, ttl: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> None:
        raise NotImplementedError
