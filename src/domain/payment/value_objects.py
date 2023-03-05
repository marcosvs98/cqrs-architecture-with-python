from typing import Union
from domain.base.value_object import StrIdValueObject


class PaymentId(StrIdValueObject):
    value: Union[str, 'PaymentId']
