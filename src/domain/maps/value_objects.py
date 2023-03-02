from enum import Enum
from domain.base.value_object import ValueObject
from pydantic import validator


class StatesEnum(str, Enum):
    RS: str = 'Rio Grande do Sul'
    SP: str = 'São Paulo'
    SC: str = 'Santa Catarina'

    @classmethod
    def has_value(cls, value):
        return value in cls._member_map_.values()


class State(ValueObject):
    enum: str = StatesEnum

    def states(self) -> bool:
        return self.value in [state.value for state in StatesEnum]

    @validator('enum', check_fields=False)
    def validate(cls, value):
        if not StatesEnum.has_value(value):
            raise ValueError(f'State named "{value}" not exists')
        return value


class Address(ValueObject):
    house_number: str
    road: str
    sub_district: str
    district: str
    state: str
    postcode: str
    country: str

    def states(self) -> bool:
        return self.state.states()
