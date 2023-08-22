import abc


class OrderMediatorInterface(abc.ABC):
    """
    The Mediator interface declares a method used by components to notify the
    mediator about various events. The Mediator may react to these events and
    pass the execution to other components.
    """

    @abc.abstractmethod
    def publish_event(self, sender: object, event: str) -> None:
        pass



class AbstractComponent(metaclass=abc.ABCMeta):
    """
    The Base Component provides the basic functionality of storing a mediator's
    instance inside component objects.
    """
    sourcing = {}

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



class OrderQueryInterface(AbstractComponent):
    @abc.abstractmethod
    def from_id(self, object_id: int) -> str:
        raise NotImplementedError


class OrderCommandInterface(AbstractComponent):
    @abc.abstractmethod
    def create(self, object_id: int, text: str) -> None:
        raise NotImplementedError


# applications

class OrderQuery(OrderQueryInterface):
    def from_id(self, object_id: int) -> str:
        try:
            return self.sourcing[object_id]
        except KeyError:
            raise KeyError(f'Object Id {object_id} not found.')


class OrderCommand(OrderCommandInterface):
    def create(self, object_id: int, text: str) -> None:
        self.sourcing[object_id] = text
        self.mediator.publish_event(self, f'Object with Id {object_id} was been created.')



class OrderMediator(OrderMediatorInterface):
    def __init__(
        self,
        command: OrderCommandInterface,
        query: OrderQueryInterface
    ) -> None:
        self._command = command
        self._command.mediator = self
        self._query = query
        self._query.mediator = self

    def create_order(self, object_id: int, text: str) -> None:
        self._command.create(object_id=object_id, text=text)

    def get_order_from_id(self, object_id: int) -> str:
        return self._query.from_id(object_id=object_id)

    def publish_event(self, sender: object, event: str) -> None:
        print(f'{sender} - published: {event}')


if __name__ == '__main__':
    # The client code.

    order_mediator = OrderMediator(
        command=OrderCommand(),
        query=OrderQuery()
    )

    order_mediator.create_order(1, '<Product>')

    text = order_mediator.get_order_from_id(1)
    print(text)
