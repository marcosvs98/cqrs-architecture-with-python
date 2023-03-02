from enum import Enum
from typing import Union

from pydantic import validator
from domain.base.value_object import ValueObject, StrIdValueObject


class OrderStatusEnum(str, Enum):
    WAITING: str = 'waiting'
    PAID: str = 'paid'
    CANCELLED: str = 'cancelled'

    @classmethod
    def has_value(cls, value):
        return value in cls._member_map_.values()


class BuyerId(StrIdValueObject):
    value: Union[str, 'BuyerId']


class OrderItem(ValueObject):
    product_id: str
    amount: int

    @validator('amount', pre=False, check_fields=False)
    def validate_amount(cls, value):
        if value < 0:
            raise ValueError(f'Expected OrderAmount >= 0, got {value}')
        return value


class OrderId(StrIdValueObject):
    value: Union[str, 'OrderId']


class OrderStatus(ValueObject):
    Enum = OrderStatusEnum
    status: str

    def __init__(self, status):
        super().__init__(status=status)

    def is_waiting(self) -> bool:
        return self.status == OrderStatus.Enum.WAITING

    def is_paid(self) -> bool:
        return self.status == OrderStatus.Enum.PAID

    def is_cancelled(self) -> bool:
        return self.status == OrderStatus.Enum.CANCELLED

    @validator('status', check_fields=False)
    def validate(cls, value):
        if not OrderStatusEnum.has_value(value):
            raise ValueError(f'OrderStatus named "{value}" not exists')
        return value
