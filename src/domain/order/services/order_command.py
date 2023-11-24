from domain.base.ports.event_adapter_interface import DomainEventPublisher
from domain.delivery.ports.cost_calculator_interface import DeliveryCostCalculatorAdapterInterface
from domain.maps.model.value_objects import Address
from domain.order.model.entities import Order
from domain.order.model.events import OrderCancelled, OrderCreated, OrderPaid
from domain.order.model.value_objects import BuyerId, OrderId, OrderItem
from domain.order.ports.order_aggregate_repository_interface import (
    OrderAggregateRepositoryInterface,
)
from domain.order.ports.order_command_interface import OrderCommandInterface
from domain.payment.ports.payment_adapter_interface import PaymentAdapterInterface
from domain.product.ports.product_adapter_interface import ProductAdapterInterface


class OrderCommand(OrderCommandInterface):
    """Handles commands related to order operations, such as  creating,
    paying, and canceling orders."""

    def __init__(
        self,
        repository: OrderAggregateRepositoryInterface,
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
        self, order_id: OrderId, buyer_id: BuyerId, items: list[OrderItem], destination: Address
    ) -> None:

        product_counts = [(item.product_id, int(item.amount)) for item in items]
        total_product_cost = await self.product_service.total_price(product_counts)
        payment_id = await self.payment_service.new_payment(total_product_cost)
        delivery_cost = await self.delivery_service.calculate_cost(total_product_cost, destination)

        order = Order(
            order_id=order_id,
            buyer_id=buyer_id,
            items=items,
            product_cost=float(total_product_cost),
            delivery_cost=float(delivery_cost),
            payment_id=payment_id,
        )
        await self.repository.save(order)
        await self.mediator.cache_repository.save(order)

        event = OrderCreated(aggregate=order)

        await self.event_publisher.publish(event)

    async def pay_order(self, order_id: OrderId) -> None:
        order = await self.repository.from_id(order_id=order_id)
        payment_id = order.payment_id

        is_payment_verified = await self.payment_service.verify_payment(payment_id=payment_id)
        await self._pay_order_tnx(order_id, is_payment_verified)

    async def cancel_order(self, order_id: OrderId) -> None:
        order = await self.repository.from_id(order_id)
        order.cancel()

        await self.repository.save(order)
        await self.mediator.cache_repository.save(order)
        event = OrderCancelled(aggregate=order)

        await self.event_publisher.publish(event)

    async def _pay_order_tnx(self, order_id, is_payment_verified) -> None:
        order = await self.repository.from_id(order_id=order_id)
        order.pay(is_payment_verified=is_payment_verified)

        await self.repository.save(order)
        await self.mediator.cache_repository.save(order)
        event = OrderPaid(aggregate=order)

        await self.event_publisher.publish(event)
