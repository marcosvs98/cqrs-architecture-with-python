from enum import Enum

from pydantic import Field

from domain.base.event import DomainEvent


class OrderEventName(Enum):

    CREATED = 'payment_order_created'
    CANCELLED = 'payment_order_cancelled'
    PAID = 'payment_order_paid'


class OrderCreated(DomainEvent):
    event_name: str = Field(OrderEventName.CREATED.value)


class OrderPaid(DomainEvent):
    event_name: str = Field(OrderEventName.PAID.value)


class OrderCancelled(DomainEvent):
    event_name: str = Field(OrderEventName.CANCELLED.value)


class OrderEvent(Enum):
    """Domain Event raised for special order use cases"""

    CREATED = 'CREATED'
    CANCELLED = 'CANCELLED'
    PAID = 'PAID'
