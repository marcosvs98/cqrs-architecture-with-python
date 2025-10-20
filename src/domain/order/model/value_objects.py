from decimal import Decimal
from enum import Enum
from typing import Annotated

from pydantic import ValidationInfo, field_validator

from domain.base.value_object import StrIdValueObject, ValueObject
from domain.product.model.value_objects import ProductId


class OrderStatusEnum(str, Enum):
    """Enumeration of possible order statuses."""

    WAITING = 'waiting'
    PAID = 'paid'
    CANCELLED = 'cancelled'
    PAYMENT_REJECTED = 'payment_rejected'
    CANCELLATION_REJECTED = 'cancellation_rejected'

    def __str__(self) -> str:
        return self.value

    @classmethod
    def has_value(cls, value: str) -> bool:
        """Return True if a given string corresponds to a valid enum value."""
        return value in (member.value for member in cls)


class BuyerId(StrIdValueObject):
    """Value object representing a buyer identifier."""


class OrderItem(ValueObject):
    """Value object representing an item in an order."""

    product_id: Annotated[str, ProductId]
    amount: Decimal

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, value: Decimal, info: ValidationInfo) -> Decimal:
        if value < 0:
            raise ValueError(f"Expected Order.amount >= 0, got {value}")
        return value


class OrderId(StrIdValueObject):
    """Value object representing an order identifier."""
