from typing import Union
from domain.base.value_object import StrIdValueObject


class ProductId(StrIdValueObject):
    id: Union[str, 'ProductId']
