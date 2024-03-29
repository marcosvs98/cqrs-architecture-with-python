import logging

from domain.order.model.entities import Order
from domain.order.model.value_objects import OrderId
from domain.order.ports.order_aggregate_repository_interface import (
    OrderAggregateRepositoryInterface,
)
from domain.order.ports.store_connector_adapter_interface import StoreConnectorAdapterInterface

logger = logging.getLogger(__name__)


class OrderAggregateRepository(OrderAggregateRepositoryInterface):
    """Repository for storing and retrieving order aggregates."""

    def __init__(self, db_connection: StoreConnectorAdapterInterface, collection_name: str):
        self.db_connection = db_connection
        self.collection_name = collection_name

    async def from_id(self, order_id: OrderId) -> Order | None:
        connection = await self.db_connection.get_connection()
        document = await connection[self.collection_name].find_one({'_id': order_id})
        if document:
            logger.info(f'Retrieved aggregate with ID: {order_id}')
            return Order.model_validate(document)
        return None

    async def save(self, order: Order) -> None:
        connection = await self.db_connection.get_connection()

        # Obtain the current aggregate from the database
        current_order = await self.from_id(order.order_id)

        if current_order:
            if current_order.version > order.version:
                error_message = (
                    f'Cannot save the aggregate with ID: {order.order_id}. '
                    f'Existing aggregate version {current_order.version} is '
                    f'equal or greater than the new version {order.version}.'
                )
                raise ValueError(error_message)

            order.version = current_order.version

        order.increase_version()

        try:
            await connection[self.collection_name].replace_one(
                {'_id': order.order_id}, order.model_dump(), upsert=True
            )
            logger.info(f'Successfully saved aggregate with ID: {order.order_id}')
        except Exception as e:
            logger.error(f'Error saving aggregate with ID: {order.order_id}')
            raise e

    async def delete(self, order_id: OrderId) -> None:
        connection = await self.db_connection.get_connection()
        await connection[self.collection_name].delete_one({'_id': order_id})
        logger.info(f'Deleted aggregate with ID: {order_id}')
