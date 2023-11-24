from typing import Any, TypeVar, Union

from pydantic import ConfigDict, GetCoreSchemaHandler, ValidationError, ValidationInfo
from pydantic_core import CoreSchema, core_schema

from domain.base.model import Model

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

    model_config = ConfigDict(arbitrary_types_allowed=True)


class StrIdValueObject(str):
    """Base class for string value objects"""

    value: Union[str, 'StrIdValueObject']

    def __init__(self, value: Union[str, 'StrIdValueObject'], field_name: str | None = None):
        self.value = value
        self.field_name = field_name

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def validate(
        cls, value: Union[str, 'StrIdValueObject'], info: ValidationInfo
    ) -> 'StrIdValueObject':
        if isinstance(value, str):
            return value
        raise ValidationError()

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.with_info_after_validator_function(
            cls.validate, handler(str), field_name=handler.field_name
        )
