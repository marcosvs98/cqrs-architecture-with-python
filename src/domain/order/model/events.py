from enum import Enum

from domain.base.event import DomainEvent


class OrderEventName(str, Enum):
    """Enumeration of domain events related to order lifecycle."""

    CREATED = 'payment_order_created'
    CANCELLED = 'payment_order_cancelled'
    PAID = 'payment_order_paid'
    PAYMENT_REJECTED = 'payment_order_rejected'
    CANCELLATION_REJECTED = 'payment_order_cancellation_rejected'

    def __str__(self) -> str:
        return self.value


class OrderCreated(DomainEvent):
    """Event emitted when an order is created."""

    event_name: str = OrderEventName.CREATED.value


class OrderPaid(DomainEvent):
    """Event emitted when an order is paid."""

    event_name: str = OrderEventName.PAID.value


class OrderCancelled(DomainEvent):
    """Event emitted when an order is cancelled."""

    event_name: str = OrderEventName.CANCELLED.value


class OrderPaymentRejected(DomainEvent):
    """Event emitted when an order payment fails verification."""

    event_name: str = OrderEventName.PAYMENT_REJECTED.value


class OrderCancellationRejected(DomainEvent):
    """Event emitted when an order cancellation attempt is rejected."""

    event_name: str = OrderEventName.CANCELLATION_REJECTED.value
