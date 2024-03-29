from bson.objectid import ObjectId

from domain.maps.model.value_objects import Address
from domain.order.model.entities import Order
from domain.order.model.value_objects import BuyerId, OrderId, OrderItem
from domain.order.ports.order_aggregate_repository_interface import (
    OrderAggregateRepositoryInterface,
)
from domain.order.ports.order_command_interface import OrderCommandInterface  # noqa: E501
from domain.order.ports.order_mediator_interface import OrderMediatorInterface  # noqa: E501
from domain.order.ports.order_query_interface import OrderQueryInterface  # noqa: E501


class OrderMediator(OrderMediatorInterface):
    """Mediates communication between the order command
    and query interfaces."""

    def __init__(
        self,
        command: OrderCommandInterface,
        query: OrderQueryInterface,
        cache_repository: OrderAggregateRepositoryInterface,
    ) -> None:
        self.cache_repository = cache_repository
        self._command = command
        self._command.mediator = self
        self._query = query
        self._query.mediator = self

    async def next_identity(self) -> OrderId:
        return OrderId(str(ObjectId()))

    async def create_new_order(
        self, buyer_id: BuyerId, items: list[OrderItem], destination: Address
    ) -> OrderId:

        order_id = await self.next_identity()

        await self._command.create_new_order(
            order_id=order_id, buyer_id=buyer_id, items=items, destination=destination
        )

        return order_id

    async def pay_order(self, order_id: OrderId):
        await self._command.pay_order(order_id=order_id)

    async def cancel_order(self, order_id: OrderId):
        await self._command.cancel_order(order_id=order_id)

    async def get_order_from_id(self, order_id: OrderId) -> Order:
        return await self._query.get_order_from_id(order_id=order_id)
