from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import ConfigDict, Field

from domain.base.dto import DataTransferObject
from domain.base.event import DomainEvent
from domain.order.model.entities import Order
from domain.order.model.value_objects import BuyerId, OrderId, OrderItem, OrderStatusEnum
from domain.payment.model.value_objects import PaymentId


class OrderReadModel(DataTransferObject):
    """Projection of an order aggregate dedicated to query/read operations."""

    order_id: OrderId = Field(alias='_id', serialization_alias='_id')
    buyer_id: BuyerId
    payment_id: PaymentId
    items: list[OrderItem]
    status: OrderStatusEnum
    product_cost: Decimal
    delivery_cost: Decimal
    total_cost: Decimal
    updated_at: datetime

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        frozen=True,
    )

    @classmethod
    def from_order(cls, order: Order, event: DomainEvent) -> OrderReadModel:
        """Build a projection from an order aggregate and its triggering event."""
        return cls.model_validate(
            {
                '_id': order.id,
                'buyer_id': order.buyer_id,
                'payment_id': order.payment_id,
                'items': list(order.items),
                'status': order.status,
                'product_cost': order.product_cost,
                'delivery_cost': order.delivery_cost,
                'total_cost': order.total_cost,
                'updated_at': event.datetime,
            }
        )
