import abc

from domain.order.model.entities import Order
from domain.order.model.value_objects import OrderId
from domain.order.ports.order_aggregate_repository_interface import (
    OrderAggregateRepositoryInterface,
)
from domain.order.ports.order_mediator_interface import AbstractComponent  # noqa: E501


class OrderQueryInterface(AbstractComponent):
    """Interface for querying orders."""

    @abc.abstractmethod
    def __init__(self, repository: OrderAggregateRepositoryInterface):
        raise NotImplementedError

    @abc.abstractmethod
    async def get_order_from_id(self, order_id: OrderId) -> Order:
        raise NotImplementedError
