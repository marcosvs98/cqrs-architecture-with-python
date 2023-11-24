import abc

from domain.maps.model.value_objects import Address
from domain.order.model.entities import Order
from domain.order.model.value_objects import BuyerId, OrderId, OrderItem


class OrderMediatorInterface(abc.ABC):
    """The Mediator interface declares a method used by components to notify the
    mediator about various events. The Mediator may react to these events and
    pass the execution to other components."""

    @abc.abstractmethod
    async def next_identity(self) -> OrderId:
        raise NotImplementedError

    @abc.abstractmethod
    async def create_new_order(
        self, buyer_id: BuyerId, items: list[OrderItem], destination: Address
    ) -> OrderId:
        raise NotImplementedError

    @abc.abstractmethod
    async def pay_order(self, order_id: OrderId):
        raise NotImplementedError

    @abc.abstractmethod
    async def cancel_order(self, order_id: OrderId):
        raise NotImplementedError

    @abc.abstractmethod
    async def get_order_from_id(self, order_id: OrderId) -> Order:
        raise NotImplementedError


class AbstractComponent(metaclass=abc.ABCMeta):
    """The Base Component provides the basic functionality of storing a mediator's
    instance inside component objects."""

    def __init__(self, mediator: OrderMediatorInterface = None) -> None:
        self._mediator = mediator

    @property
    def mediator(self) -> OrderMediatorInterface:
        return self._mediator

    @mediator.setter
    def mediator(self, mediator: OrderMediatorInterface) -> None:
        self._mediator = mediator

    def __repr__(self):
        return type(self).__name__
