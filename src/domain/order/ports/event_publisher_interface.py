import abc

from domain.base.event import DomainEvent


class EventPublisherInterface(abc.ABC):
    @abc.abstractmethod
    async def publish_event(self, event: DomainEvent) -> None:
        raise NotImplementedError
