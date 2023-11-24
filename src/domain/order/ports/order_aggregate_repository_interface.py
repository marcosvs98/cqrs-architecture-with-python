import abc

from domain.order.model.entities import Order
from domain.order.model.value_objects import OrderId
from domain.order.ports.store_connector_adapter_interface import StoreConnectorAdapterInterface


class OrderAggregateRepositoryInterface(abc.ABC):
    """Interface for managing order aggregates."""

    def __init__(self, db_connection: StoreConnectorAdapterInterface, collection_name: str):
        self.db_connection = db_connection
        self.collection_name = collection_name

    @abc.abstractmethod
    async def from_id(self, order_id: OrderId) -> Order | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def save(self, order: Order) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, order_id: OrderId) -> None:
        raise NotImplementedError
