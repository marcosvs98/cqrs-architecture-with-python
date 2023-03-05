from domain.order.value_objects import OrderId
from domain.order.entities import Order
from domain.order.ports.order_query_interface import OrderQueryInterface  # noqa: E501
from domain.order.ports.order_database_interface import OrderDatabaseInterface  # noqa: E501


class OrderQuery(OrderQueryInterface):

    repository: OrderDatabaseInterface

    def __init__(self, repository: OrderDatabaseInterface):
        self.repository = repository

    async def get_order_from_id(self, order_id: OrderId) -> Order:
        try:
            return await self.mediator.cache.get(key=order_id)
        except:
            return await self.repository.from_id(order_id)
