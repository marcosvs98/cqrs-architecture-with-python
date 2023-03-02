import abc
from typing import List
from domain.order.value_objects import OrderId
from domain.order.entities import Order


class OrderDatabaseInterface(abc.ABC):
    @abc.abstractmethod
    def __init__(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def next_identity(self) -> OrderId:
        raise NotImplementedError

    @abc.abstractmethod
    async def all(self) -> List[Order]:
        raise NotImplementedError

    @abc.abstractmethod
    async def from_id(self, id_: OrderId) -> Order:
        raise NotImplementedError

    @abc.abstractmethod
    async def save(self, entity: Order):
        raise NotImplementedError
