import abc

from domain.base.entity import AggregateRoot
from domain.base.event import DomainEvent
from domain.order.model.value_objects import OrderId


class OrderEventStoreRepositoryInterface(abc.ABC):
    """Interface for managing order context events."""

    @abc.abstractmethod
    async def from_id(self, order_id: OrderId) -> AggregateRoot | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def save(self, event: DomainEvent) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_all_events_by_tracker_id(self, tracker_id: str) -> list[DomainEvent]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_last_event_version_from_entity(self, order_id: OrderId) -> DomainEvent | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def rebuild_aggregate_root(
        self, event: DomainEvent, aggregate_class: AggregateRoot
    ) -> AggregateRoot:
        raise NotImplementedError
