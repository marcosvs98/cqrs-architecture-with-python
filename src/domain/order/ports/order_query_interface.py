import abc
from domain.order.value_objects import OrderId
from domain.order.entities import Order
from domain.order.ports.order_database_interface import OrderDatabaseInterface  # noqa: E501
from domain.order.ports.order_mediator_interface import AbstractComponent  # noqa: E501


class OrderQueryInterface(AbstractComponent):

    repository: OrderDatabaseInterface

    @abc.abstractmethod
    def __init__(self, repository: OrderDatabaseInterface):
        raise NotImplementedError

    @abc.abstractmethod
    async def get_order_from_id(self, order_id: OrderId) -> Order:
        raise NotImplementedError