import abc
from typing import Union

from domain.base.entity import AggregateRoot
from domain.base.event import DomainEvent
from domain.order.value_objects import OrderId


class OrderEventStoreRepositoryInterface(abc.ABC):
    @abc.abstractmethod
    async def from_id(self, order_id: OrderId) -> Union[AggregateRoot, None]:
        raise NotImplementedError

    @abc.abstractmethod
    async def save(self, event: DomainEvent) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_all_events_by_tracker_id(self, tracker_id: str) -> list[DomainEvent]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_last_event_version_from_entity(
        self, order_id: OrderId
    ) -> Union[DomainEvent, None]:
        raise NotImplementedError

    @abc.abstractmethod
    async def rebuild_aggregate_root(
        self, event: DomainEvent, aggregate_class: AggregateRoot
    ) -> AggregateRoot:
        raise NotImplementedError
