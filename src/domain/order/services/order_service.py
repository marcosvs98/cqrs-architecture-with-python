from typing import List

from domain.order.value_objects import BuyerId, OrderItem, OrderId
from domain.order.entities import Order
from domain.maps.value_objects import Address

from domain.order.ports.order_service_interface import OrderServiceInterface  # noqa: E501
from domain.order.ports.order_database_interface import OrderDatabaseInterface  # noqa: E501
from domain.payment.ports.payment_adapter_interface import PaymentAdapterInterface  # noqa: E501
from domain.product.ports.product_adapter_interface import ProductAdapterInterface  # noqa: E501
from domain.delivery.ports.cost_calculator_interface import (
    DeliveryCostCalculatorAdapterInterface,
)  # noqa: E501
from domain.base.ports.event_adapter_interface import DomainEventPublisher
from domain.order.events import OrderCreated, OrderPaid, OrderCancelled


class OrderService(OrderServiceInterface):

    repository: OrderDatabaseInterface

    def __init__(
        self,
        repository: OrderDatabaseInterface,
        payment_service: PaymentAdapterInterface,
        product_service: ProductAdapterInterface,
        delivery_service: DeliveryCostCalculatorAdapterInterface,
        event_publisher: DomainEventPublisher,
    ):
        self.repository = repository
        self.payment_service = payment_service
        self.product_service = product_service
        self.delivery_service = delivery_service
        self.event_publisher = event_publisher

    async def create_new_order(
        self, buyer_id: BuyerId, items: List[OrderItem], destination: Address
    ) -> OrderId:

        product_counts = [(item.product_id, int(item.amount)) for item in items]
        total_product_cost = await self.product_service.total_price(product_counts)
        payment_id = await self.payment_service.new_payment(total_product_cost)
        delivery_cost = await self.delivery_service.calculate_cost(total_product_cost, destination)
        order_id = await self.repository.next_identity()

        order = Order(
            order_id=order_id,
            buyer_id=buyer_id,
            items=items,
            product_cost=float(total_product_cost),
            delivery_cost=float(delivery_cost),
            payment_id=payment_id,
        )
        await self.repository.save(order)

        event = OrderCreated(
            order_id=order_id,
            buyer_id=buyer_id,
            items=items,
            product_cost=total_product_cost,
            delivery_cost=delivery_cost,
            payment_id=payment_id,
            destination=destination,
        )

        await self.event_publisher.publish(event)

        return order.order_id

    async def pay_order(self, order_id: OrderId):
        order = await self.repository.from_id(order_id=order_id)
        payment_id = order.payment_id

        is_payment_verified = await self.payment_service.verify_payment(payment_id=payment_id)
        await self._pay_order_tnx(order_id, is_payment_verified)

    async def cancel_order(self, order_id: OrderId):
        order = await self.repository.from_id(order_id)
        order.cancel()

        event = OrderCancelled(
            order_id=order.order_id,
            buyer_id=order.buyer_id,
            items=order.items,
            product_cost=order.product_cost,
            delivery_cost=order.delivery_cost,
            payment_id=order.payment_id,
            version=order.version,
        )

        await self.event_publisher.publish(event)
        await self.repository.save(order)

    async def get_order_from_id(self, order_id: OrderId) -> Order:
        return await self.repository.from_id(order_id)

    async def _pay_order_tnx(self, order_id, is_payment_verified):
        order = await self.repository.from_id(order_id=order_id)
        order.pay(is_payment_verified=is_payment_verified)

        event = OrderPaid(
            order_id=order.order_id,
            buyer_id=order.buyer_id,
            items=order.items,
            product_cost=order.product_cost,
            delivery_cost=order.delivery_cost,
            payment_id=order.payment_id,
            version=order.version,
        )
        await self.event_publisher.publish(event)
        await self.repository.save(order)
