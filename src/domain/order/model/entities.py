from collections.abc import Sequence
from decimal import Decimal

from pydantic import Field

from domain.base.entity import AggregateRoot
from domain.order.exceptions.order_exceptions import (
    OrderAlreadyCancelledException,
    OrderAlreadyPaidException,
    PaymentNotVerifiedException,
)
from domain.order.model.value_objects import BuyerId, OrderId, OrderItem, OrderStatusEnum
from domain.payment.model.value_objects import PaymentId
from domain.utils import make_id_generator


class Order(AggregateRoot):
    """Aggregate root representing an order."""

    id: OrderId = Field(default_factory=make_id_generator('order'))
    buyer_id: BuyerId
    items: Sequence[OrderItem]
    product_cost: Decimal
    delivery_cost: Decimal
    payment_id: PaymentId
    status: OrderStatusEnum = OrderStatusEnum.WAITING

    def pay(self, is_payment_verified: bool) -> None:
        if self.is_cancelled():
            raise OrderAlreadyCancelledException(detail='order already cancelled')
        if self.is_paid():
            raise OrderAlreadyPaidException(detail='order already paid')
        if not is_payment_verified:
            raise PaymentNotVerifiedException(detail=f"payment {self.payment_id} not verified")
        self.status = OrderStatusEnum.PAID

    def cancel(self) -> None:
        if self.is_cancelled():
            raise OrderAlreadyCancelledException(detail='order already cancelled')
        if self.is_paid():
            raise OrderAlreadyPaidException(detail='order already paid')
        self.status = OrderStatusEnum.CANCELLED

    def reject_payment(self) -> None:
        if self.is_paid():
            raise OrderAlreadyPaidException(detail='order already paid')
        self.status = OrderStatusEnum.PAYMENT_REJECTED

    def reject_cancellation(self) -> None:
        if self.is_cancelled():
            raise OrderAlreadyCancelledException(detail='order already cancelled')
        self.status = OrderStatusEnum.CANCELLATION_REJECTED

    def is_waiting(self) -> bool:
        return self.status is OrderStatusEnum.WAITING

    def is_paid(self) -> bool:
        return self.status is OrderStatusEnum.PAID

    def is_cancelled(self) -> bool:
        return self.status is OrderStatusEnum.CANCELLED

    @property
    def total_cost(self) -> Decimal:
        return self.product_cost + self.delivery_cost
