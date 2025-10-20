from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError

from domain.base.event import DomainEvent
from domain.order.exceptions.order_exceptions import EntityOutdated, PersistenceError
from domain.order.model.entities import Order
from domain.order.model.value_objects import OrderId
from domain.order.ports.order_event_store_repository_interface import (
    OrderEventStoreRepositoryInterface,
)
from utils.logger import get_logger

logger = get_logger()


class OrderEventStoreRepository(OrderEventStoreRepositoryInterface):
    """Repository for storing and retrieving order domain events using event sourcing."""

    async def from_id(self, order_id: OrderId) -> list[DomainEvent] | None:
        """Load all domain events for a given aggregate id."""
        async with self.db_connection.get_connection() as connection:
            cursor = connection[self.collection_name].find({'aggregate.id': str(order_id)})
            events_list = await cursor.to_list(length=None)
            if not events_list:
                return None
            return [DomainEvent.model_validate(event) for event in events_list]

    async def save(self, event: DomainEvent) -> None:
        """Persist a new domain event with optimistic concurrency checks."""
        order = event.aggregate
        last_event = await self.get_last_event_version_from_entity(order.id)

        if last_event:
            order_old = Order.model_validate(last_event.aggregate)
            if order_old and order_old.version > order.version:
                raise EntityOutdated(
                    detail=f"incoming version {order.version} "
                    f"is behind current {order_old.version}"
                )
            event = event.model_copy(
                update={
                    'version': last_event.version + 1,
                    'tracker_id': last_event.tracker_id,
                }
            )
        else:
            event = event.model_copy(update={'version': 1})

        async with self.db_connection.get_connection() as connection:
            try:
                await connection[self.collection_name].insert_one(event.model_dump(mode='json'))
            except DuplicateKeyError as exc:
                await logger.exception(
                    'Duplicate event detected',
                    event_id=str(event.id),
                    collection=self.collection_name,
                )
                raise PersistenceError(detail=f"duplicate event id {event.id}") from exc

    async def get_all_events_by_tracker_id(self, tracker_id: str) -> list[DomainEvent]:
        """Retrieve all events correlated by a tracker id."""
        async with self.db_connection.get_connection() as connection:
            cursor = connection[self.collection_name].find({'tracker_id': tracker_id})
            events_list = await cursor.to_list(length=None)
            return (
                [DomainEvent.model_validate(event) for event in events_list] if events_list else []
            )

    async def get_last_event_version_from_entity(self, order_id: OrderId) -> DomainEvent | None:
        """Return the most recent event for a given aggregate id."""
        async with self.db_connection.get_connection() as connection:
            cursor = connection[self.collection_name].find(
                {'aggregate.id': str(order_id)},
                sort=[('version', -1)],
                limit=1,
            )
            events_list = await cursor.to_list(length=None)
            if not events_list:
                return None
            event = events_list[0]
            event.pop('_id', None)
            return DomainEvent.model_validate(event)

    async def rebuild_aggregate_root(
        self, event: DomainEvent, aggregate_class: type[Order]
    ) -> Order:
        """Rehydrate an aggregate from a domain event."""
        try:
            return aggregate_class.model_validate(event.aggregate)
        except ValidationError as exc:
            await logger.error(
                'Invalid aggregate reconstruction',
                aggregate_type=aggregate_class.__name__,
                event_id=str(event.id),
                error=str(exc),
            )
            raise PersistenceError(detail='invalid aggregate reconstruction') from exc
