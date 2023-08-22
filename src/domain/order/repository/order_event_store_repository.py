import logging
from typing import Union

from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError

from domain.base.entity import AggregateRoot
from domain.base.event import DomainEvent
from domain.order.ports.order_event_store_repository_interface import \
    OrderEventStoreRepositoryInterface
from domain.order.ports.store_connector_adapter_interface import \
    StoreConnectorAdapterInterface
from domain.order.value_objects import OrderId

logger = logging.getLogger(__name__)


class OrderEventStoreRepository(OrderEventStoreRepositoryInterface):
    """
    Repository for storing and retrieving vehicle domain
    events using event sourcing.
    """

    def __init__(self, db_connection: StoreConnectorAdapterInterface, collection_name: str):
        self.db_connection = db_connection
        self.collection_name = collection_name

    async def from_id(self, order_id: OrderId) -> Union[AggregateRoot, None]:
        connection = await self.db_connection.get_connection()
        events = []
        result = connection[self.collection_name].find({'order_id': order_id})
        events_list = await result.to_list(length=None)
        if events_list:
            logger.info(f'Retrieved all events for order_id: {order_id}')
            events = [DomainEvent.parse_obj(event) for event in events_list]
        return events or None

    async def save(self, event: DomainEvent) -> None:
        aggregate_root = event.aggregate

        event_old = await self.get_last_event_version_from_entity(aggregate_root.order_id)
        if event_old:
            aggregate_root_old = event_old.aggregate

            if aggregate_root_old and aggregate_root_old.version > aggregate_root.version:
                error_message = (
                    f'Aggregate Root version needs to be greater than '
                    f'the current one: {aggregate_root.version} > {aggregate_root_old.version}.'
                )
                logger.warning(error_message, exc_info=True)
                raise ValueError(error_message)

            event.version = event_old.version
            event.increase_version()
            event.tracker_id = event_old.tracker_id
        else:
            event.increase_version()

        connection = await self.db_connection.get_connection()
        try:
            await connection[self.collection_name].insert_one(event.to_dict())
            logger.info(f'Successfully saved event with ID: {event.id}')
        except DuplicateKeyError as e:
            error_message = f'Duplicate event found with ID: {event.id}'
            raise e from e

    async def get_all_events_by_tracker_id(self, tracker_id: str) -> list[DomainEvent]:
        connection = await self.db_connection.get_connection()
        events = []
        result = connection[self.collection_name].find({'tracker_id': tracker_id})
        events_list = await result.to_list(length=None)
        if events_list:
            logger.info(f'Retrieved all events for tracker_id: {tracker_id}')
            events = [DomainEvent.parse_obj(event) for event in events_list]
        return events

    async def get_last_event_version_from_entity(
        self, order_id: OrderId
    ) -> Union[DomainEvent, None]:
        connection = await self.db_connection.get_connection()
        events = connection[self.collection_name].find(
            {'data.order_id': order_id}, sort=[('version', -1)], limit=1
        )
        events_list = await events.to_list(length=None)
        if events_list:
            event = events_list[0]
            event.pop('_id', None)
            logger.info(
                f'Retrieved last aggregate version event for order id: {order_id}'
            )
            return DomainEvent.parse_obj(event)
        return None

    async def rebuild_aggregate_root(
        self, event: DomainEvent, aggregate_class: AggregateRoot
    ) -> AggregateRoot:
        try:
            aggregate_root = aggregate_class.parse_obj(event.aggregate.dict())
        except ValidationError as e:
            logger.error(f'Error rebuilding aggregate root from event: {event.id}')
            raise e
        logger.info(f'Aggregate root rebuilt successfully from event: {event.id}')
        return aggregate_root
