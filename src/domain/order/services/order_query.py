from domain.order.exceptions.order_exceptions import EntityNotFound
from domain.order.model.entities import Order
from domain.order.model.value_objects import OrderId
from domain.order.ports.order_aggregate_repository_interface import (
    OrderAggregateRepositoryInterface,
)
from domain.order.ports.order_query_interface import OrderQueryInterface  # noqa: E501


class OrderQuery(OrderQueryInterface):
    """Handles queries for retrieving order information."""

    def __init__(self, repository: OrderAggregateRepositoryInterface):
        self.repository = repository

    async def get_order_from_id(self, order_id: OrderId) -> Order:
        try:
            order = await self.mediator.cache_repository.from_id(order_id=order_id)
        except EntityNotFound:
            order = await self.repository.from_id(order_id)
        return order
