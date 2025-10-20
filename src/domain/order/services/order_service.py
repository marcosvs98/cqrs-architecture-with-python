from decimal import Decimal
from typing import Annotated

from domain.base.event import DomainEvent
from domain.maps.model.value_objects import Address
from domain.order.exceptions.order_exceptions import (
    OrderAlreadyPaidException,
    OrderNotFound,
    PaymentNotVerifiedException,
)
from domain.order.model.entities import Order
from domain.order.model.events import (
    OrderCancellationRejected,
    OrderCancelled,
    OrderCreated,
    OrderPaid,
    OrderPaymentRejected,
)
from domain.order.model.value_objects import BuyerId, OrderId, OrderItem
from domain.order.ports.order_service_interface import OrderServiceInterface
from utils.logger import get_logger

logger = get_logger()


class OrderService(OrderServiceInterface):
    """Application service responsible for orchestrating order operations."""

    async def create_new_order(
        self,
        buyer_id: Annotated[str, BuyerId],
        items: list[OrderItem],
        destination: Address,
    ) -> OrderId:
        """Create a new order with payment, product and delivery costs, then publish an event."""
        product_counts = [(item.product_id, int(item.amount)) for item in items]
        total_product_cost = await self.product_service.total_price(product_counts)
        payment_id = await self.payment_service.new_payment(total_product_cost)
        delivery_cost = await self.delivery_service.calculate_cost(total_product_cost, destination)

        order = Order(
            buyer_id=buyer_id,
            items=items,
            product_cost=self._to_decimal(total_product_cost),
            delivery_cost=self._to_decimal(delivery_cost),
            payment_id=payment_id,
        )
        await self.repository.save(order)
        event = OrderCreated(aggregate=order)
        await self._persist_event(order, event)
        await logger.info(
            'Order created',
            order_id=str(order.id),
            buyer_id=str(buyer_id),
            payment_id=str(payment_id),
        )
        return OrderId(order.id)

    async def pay_order(self, order_id: Annotated[str, OrderId]) -> None:
        """Verify payment and mark the order as paid, then publish an event."""
        order = await self._get_order_or_raise(order_id)
        is_payment_verified = await self.payment_service.verify_payment(payment_id=order.payment_id)

        if not is_payment_verified:
            order.reject_payment()
            await self.repository.save(order)
            event = OrderPaymentRejected(aggregate=order)
            await self._persist_event(order, event)
            await logger.warning(
                'Order payment rejected',
                order_id=str(order_id),
                payment_id=str(order.payment_id),
            )
            raise PaymentNotVerifiedException(detail=f"payment {order.payment_id} not verified")

        order.pay(is_payment_verified=is_payment_verified)
        await self.repository.save(order)
        event = OrderPaid(aggregate=order)
        await self._persist_event(order, event)
        await logger.info(
            'Order paid',
            order_id=str(order_id),
            payment_verified=is_payment_verified,
        )

    async def cancel_order(self, order_id: Annotated[str, OrderId]) -> None:
        """Cancel an order and publish an event."""
        order = await self._get_order_or_raise(order_id)

        if order.is_paid():
            order.reject_cancellation()
            await self.repository.save(order)
            event = OrderCancellationRejected(aggregate=order)
            await self._persist_event(order, event)
            await logger.warning('Order cancellation rejected', order_id=str(order_id))
            raise OrderAlreadyPaidException(detail='order already paid')

        order.cancel()
        await self.repository.save(order)
        event = OrderCancelled(aggregate=order)
        await self._persist_event(order, event)
        await logger.info(
            'Order cancelled',
            order_id=str(order_id),
            status=order.status,
        )

    async def get_order_from_id(self, order_id: Annotated[str, OrderId]) -> Order:
        """Retrieve an order by its identifier."""
        order = await self._get_order_or_raise(order_id)
        await logger.info('Order retrieved', order_id=str(order_id))
        return order

    async def _persist_event(self, order: Order, event: DomainEvent) -> None:
        await self.event_store.save(event)
        await self.read_repository.project(order, event)
        try:
            await self.event_publisher.publish(event)
        except Exception as exc:  # pragma: no cover - logging path
            await logger.warning(
                'Event publisher failure',
                event_name=event.event_name,
                tracker_id=str(event.tracker_id),
                error=str(exc),
            )

    @staticmethod
    def _to_decimal(value: Decimal | float | int | str) -> Decimal:
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))

    async def _get_order_or_raise(self, order_id: Annotated[str, OrderId]) -> Order:
        order = await self.repository.from_id(order_id)
        if order is None:
            await logger.warning('Order not found', order_id=str(order_id))
            raise OrderNotFound(detail=f"order '{order_id}' not found")
        return order
