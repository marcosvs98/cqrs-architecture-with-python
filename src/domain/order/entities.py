from typing import List

from domain.base.entity import AggregateRoot
from domain.order.exceptions.order_exceptions import (
    OrderAlreadyCancelledException, OrderAlreadyPaidException,
    PaymentNotVerifiedException)
from domain.order.value_objects import BuyerId, OrderId, OrderItem, OrderStatus
from domain.payment.value_objects import PaymentId


class Order(AggregateRoot):
    order_id: OrderId
    buyer_id: BuyerId
    items: List[OrderItem]
    product_cost: float
    delivery_cost: float
    payment_id: PaymentId
    status: OrderStatus = OrderStatus.Enum.WAITING
    version: int = 0

    def pay(self, is_payment_verified: bool):
        if self.is_cancelled():
            raise OrderAlreadyCancelledException(detail="Order's already cancelled")
        if self.is_paid():
            raise OrderAlreadyPaidException(detail="Order's already paid")
        if not is_payment_verified:
            raise PaymentNotVerifiedException(detail=f'Payment {self.payment_id} must be verified')

        self.status = OrderStatus.Enum.PAID

    def cancel(self):
        if self.is_cancelled():
            raise OrderAlreadyCancelledException(detail="Order's already cancelled")
        if self.is_paid():
            raise OrderAlreadyPaidException(detail="Order's already paid")

        self.status = OrderStatus.Enum.CANCELLED

    def is_waiting(self) -> bool:
        return self._get_order_status(self.status).is_waiting()

    def is_paid(self) -> bool:
        return self._get_order_status(self.status).is_paid()

    def is_cancelled(self) -> bool:
        return self._get_order_status(self.status).is_cancelled()

    def _get_order_status(self, value):
        return OrderStatus(value)

    @property
    def total_cost(self) -> float:
        return self.product_cost + self.delivery_cost

    def increase_version(self):
        self.version += 1

    class Config:
        arbitrary_types_allowed = True
