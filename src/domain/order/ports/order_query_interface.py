import abc

from domain.order.entities import Order
from domain.order.ports.order_aggregate_repository_interface import \
    OrderAggregateRepositoryInterface
from domain.order.ports.order_mediator_interface import \
    AbstractComponent  # noqa: E501
from domain.order.value_objects import OrderId


class OrderQueryInterface(AbstractComponent):

    @abc.abstractmethod
    def __init__(self, repository: OrderAggregateRepositoryInterface):
        raise NotImplementedError

    @abc.abstractmethod
    async def get_order_from_id(self, order_id: OrderId) -> Order:
        raise NotImplementedError
