from typing import TypeVar
from domain.base.model import Model
from pydantic import validator

ImplementationType = TypeVar('ImplementationType', bound='ValueObject')


class ValueObject(Model):
    """Base class for value objects"""

    def __eq__(self: ImplementationType, other: ImplementationType):
        if type(self) is not type(other):
            return False

        for attr_name in getattr(self, '__attrs'):
            if getattr(self, attr_name) != getattr(other, attr_name):
                return False

        return True

    class Config:
        arbitrary_types_allowed = True


class StrIdValueObject(ValueObject):
    """Base class for string value objects"""

    value: str

    def __init__(self, value):  # noqa: W0622:
        super().__init__(value=value)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.value)

    @validator('*')
    def validate(cls, value):
        if isinstance(value, StrIdValueObject):
            return str(value)
        return value
