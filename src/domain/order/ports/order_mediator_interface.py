import abc
from domain.base.ports.event_adapter_interface import DomainEventPublisher


class OrderMediatorInterface(abc.ABC):
    """
    The Mediator interface declares a method used by components to notify the
    mediator about various events. The Mediator may react to these events and
    pass the execution to other components.
    """


class AbstractComponent(metaclass=abc.ABCMeta):
    """
    The Base Component provides the basic functionality of storing a mediator's
    instance inside component objects.
    """

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
