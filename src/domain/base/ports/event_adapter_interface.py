import abc
from domain.base.event import DomainEvent


class DomainEventPublisher(metaclass=abc.ABCMeta):
    """Base domain event publisher."""

    @abc.abstractmethod
    async def publish(self, event: DomainEvent):
        raise NotImplementedError
