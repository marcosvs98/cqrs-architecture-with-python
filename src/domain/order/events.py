from enum import Enum
from typing import List
from pydantic import Field
from domain.base.event import DomainEvent
from domain.maps.value_objects import Address

from domain.payment.value_objects import PaymentId
from domain.order.value_objects import OrderId
from domain.order.value_objects import BuyerId
from domain.order.value_objects import OrderItem


class OrderEventName(Enum):

    CREATED = 'payment_order_created'
    CANCELLED = 'payment_order_cancelled'
    PAID = 'payment_order_paid'


class OrderCreated(DomainEvent):
    event_name: str = Field(OrderEventName.CREATED.value)
    order_id: OrderId
    buyer_id: BuyerId
    items: List[OrderItem]
    product_cost: float
    delivery_cost: float
    payment_id: PaymentId
    destination: Address
    version: int = 0


class OrderPaid(DomainEvent):
    event_name: str = Field(OrderEventName.PAID.value)
    order_id: OrderId
    buyer_id: BuyerId
    items: List[OrderItem]
    product_cost: float
    delivery_cost: float
    payment_id: PaymentId
    version: int = 0


class OrderCancelled(DomainEvent):
    event_name: str = Field(OrderEventName.CANCELLED.value)
    order_id: OrderId
    buyer_id: BuyerId
    items: List[OrderItem]
    product_cost: float
    delivery_cost: float
    payment_id: PaymentId
    version: int = 0


class OrderEvent(Enum):
    """Domain Event raised for special order use cases"""

    CREATED = 'CREATED'
    CANCELLED = 'CANCELLED'
    PAID = 'PAID'
