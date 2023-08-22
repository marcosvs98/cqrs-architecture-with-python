import abc
from typing import Optional

from domain.order.entities import Order
from domain.order.value_objects import OrderId
from ports.cache_interface import CacheInterface


class OrderPersistenceRepositoryInterface(abc.ABC):
    def __init__(self, cache_adapter: CacheInterface):
        self.cache_adapter = cache_adapter

    @abc.abstractmethod
    async def get_order_from_id(self, order_id: OrderId) -> Optional[Order]:
        raise NotImplementedError

    @abc.abstractmethod
    async def persist_order(self, order: Order) -> None:
        raise NotImplementedError
