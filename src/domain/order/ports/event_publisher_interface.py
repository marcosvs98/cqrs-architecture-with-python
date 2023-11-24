import abc

from domain.base.event import DomainEvent


class EventPublisherInterface(abc.ABC):
    """interface for publishing domain events."""

    @abc.abstractmethod
    async def publish_event(self, event: DomainEvent) -> None:
        raise NotImplementedError
