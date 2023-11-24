from enum import Enum
from typing import Union

from pydantic import ValidationInfo, field_validator

from domain.base.value_object import StrIdValueObject, ValueObject


class OrderStatusEnum(str, Enum):
    WAITING = 'waiting'
    PAID = 'paid'
    CANCELLED = 'cancelled'

    def __str__(self) -> str:
        return self.value

    @classmethod
    def has_value(cls, value):
        return value in cls._member_map_.values()


class BuyerId(StrIdValueObject):
    value: Union[str, 'BuyerId']


class OrderItem(ValueObject):
    product_id: str
    amount: int

    @field_validator('amount')
    @classmethod
    def validate(cls, value: str | int, info: ValidationInfo) -> 'OrderStatusEnum':
        if value < 0:
            raise ValueError(f'Expected Order.amount >= 0, got {value}')
        return value


class OrderId(StrIdValueObject):
    value: Union[str, 'OrderId']


class OrderStatus(StrIdValueObject):
    Enum = OrderStatusEnum

    def is_waiting(self) -> bool:
        return self.value == OrderStatus.Enum.WAITING

    def is_paid(self) -> bool:
        return self.value == OrderStatus.Enum.PAID

    def is_cancelled(self) -> bool:
        return self.value == OrderStatus.Enum.CANCELLED

    @field_validator('value')
    @classmethod
    def validate(cls, value: str | OrderStatusEnum, info: ValidationInfo) -> 'OrderStatusEnum':
        if not OrderStatusEnum.has_value(value):
            raise ValueError(f'OrderStatus named "{value}" not exists')
        return value
