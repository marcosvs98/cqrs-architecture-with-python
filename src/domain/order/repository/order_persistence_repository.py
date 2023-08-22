import json
import logging
from typing import Optional

import aioredis
from bson.objectid import ObjectId

import settings
from domain.order.entities import Order
from domain.order.exceptions.order_exceptions import EntityOutdated
from domain.order.ports.order_persistence_repository_interface import \
    OrderPersistenceRepositoryInterface
from domain.order.value_objects import OrderId

logger = logging.getLogger(__name__)


class OrderPersistenceRepository(OrderPersistenceRepositoryInterface):
    async def get_order_from_id(self, order_id: OrderId) -> Optional[Order]:
        try:
            logger.info(f'Getting order from cache for id: {order_id}')
            key = f'order:{order_id}'

            cached_order = await self.cache_adapter.get(key=key)

            if cached_order:
                logger.info(f'Retrieved order from cache for id: {order_id}')
                return Order.parse_obj(cached_order)
            logger.info(f'Order not found in cache for id: {order_id}')
            raise EntityNotFound()
        except (json.JSONDecodeError, aioredis.RedisError) as e:
            logger.error(f"Failed to get order from cache for id: '{order_id}''. Error: {e}")
            raise EntityOutdated(
                f"Failed to get order from cache for id: '{order_id}'. Error: {e}"
            ) from e


    async def persist_order(self, order: Order) -> None:
        try:
            await self.cache_adapter.set(key=f'order:{order.order_id}', data=order.dict())
            logger.info(f"Persisted order for id: '{order.order_id}'")
        except aioredis.RedisError as e:
            logger.error(
                f"Failed to create or update order for id: '{order.order_id}'. Error: {e}"
            )
