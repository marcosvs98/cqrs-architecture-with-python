from domain.order.entities import Order
from domain.order.ports.order_aggregate_repository_interface import \
    OrderAggregateRepositoryInterface
from domain.order.ports.order_query_interface import \
    OrderQueryInterface  # noqa: E501
from domain.order.value_objects import OrderId


class OrderQuery(OrderQueryInterface):

    def __init__(self, repository: OrderAggregateRepositoryInterface):
        self.repository = repository

    async def get_order_from_id(self, order_id: OrderId) -> Order:
        try:
            order = await self.mediator.cache_repository.get_order_from_id(order_id=order_id)
        except:
            order = await self.repository.from_id(order_id)
        return order
