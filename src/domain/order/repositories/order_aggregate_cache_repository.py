import json
import logging

import aioredis

from domain.order.exceptions.order_exceptions import (
    EntityNotFound,
    EntityOutdated,
    PersistenceError,
)
from domain.order.model.entities import Order
from domain.order.model.value_objects import OrderId
from domain.order.ports.order_aggregate_repository_interface import (
    OrderAggregateRepositoryInterface,
)
from ports.cache_interface import CacheInterface

logger = logging.getLogger(__name__)


class OrderAggregateCacheRepository(OrderAggregateRepositoryInterface):
    """Repository for storing and retrieving order aggregates."""

    def __init__(self, cache_adapter: CacheInterface):
        self.cache_adapter = cache_adapter

    async def from_id(self, order_id: OrderId) -> Order | None:
        try:
            logger.info(f'Retrieving order from cache for ID: {order_id}')
            key = f'order:{order_id}'

            cached_order = await self.cache_adapter.get(key=key)

            if cached_order:
                logger.info(f'Retrieved order from cache for ID: {order_id}')
                return Order.parse_obj(cached_order)

            logger.info(f'Order not found in cache for ID: {order_id}')
            raise EntityNotFound(f'Order with ID {order_id} not found in cache')
        except (json.JSONDecodeError, aioredis.RedisError) as e:
            error_message = (
                f'Failed to retrieve order from ' f'cache for ID: {order_id}. Error: {e}'
            )
            logger.error(error_message)
            raise EntityOutdated(error_message) from e

    async def save(self, order: Order) -> None:
        try:
            await self.cache_adapter.set(key=f'order:{order.order_id}', data=order.dict())
            logger.info(f'Saved order with ID: {order.order_id} in cache')
        except aioredis.RedisError as e:
            error_message = (
                f'Failed to persist order with ' f'ID: {order.order_id} in cache. Error: {e}'
            )
            logger.error(error_message)
            raise PersistenceError(error_message) from e

    async def delete(self, order_id: OrderId) -> None:
        try:
            await self.cache_adapter.delete(key=f'order:{order_id}')
            logger.info(f'Deleted order with ID: {order_id} in cache')
        except aioredis.RedisError as e:
            error_message = f'Failed to delete order with ' f'ID: {order_id} in cache. Error: {e}'
            raise PersistenceError(error_message) from e
