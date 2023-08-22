import abc
from typing import Optional

from domain.order.entities import Order
from domain.order.ports.store_connector_adapter_interface import \
    StoreConnectorAdapterInterface
from domain.order.value_objects import OrderId


class OrderAggregateRepositoryInterface(abc.ABC):
    def __init__(self, db_connection: StoreConnectorAdapterInterface, collection_name: str):
        self.db_connection = db_connection
        self.collection_name = collection_name

    @abc.abstractmethod
    async def from_id(self, order_id: OrderId) -> Optional[Order]:
        raise NotImplementedError

    @abc.abstractmethod
    async def save(self, order: Order) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, order_id: OrderId) -> None:
        raise NotImplementedError
