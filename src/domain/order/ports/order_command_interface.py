import abc

from domain.base.ports.event_adapter_interface import DomainEventPublisher
from domain.delivery.ports.cost_calculator_interface import (
    DeliveryCostCalculatorAdapterInterface,
)  # noqa: E501
from domain.maps.model.value_objects import Address
from domain.order.model.value_objects import BuyerId, OrderId, OrderItem
from domain.order.ports.order_aggregate_repository_interface import (
    OrderAggregateRepositoryInterface,
)
from domain.order.ports.order_mediator_interface import AbstractComponent  # noqa: E501
from domain.payment.ports.payment_adapter_interface import PaymentAdapterInterface  # noqa: E501
from domain.product.ports.product_adapter_interface import ProductAdapterInterface  # noqa: E501


class OrderCommandInterface(AbstractComponent):
    """Interface for command orders."""

    @abc.abstractmethod
    def __init__(
        self,
        repository: OrderAggregateRepositoryInterface,
        payment_service: PaymentAdapterInterface,
        product_service: ProductAdapterInterface,
        delivery_service: DeliveryCostCalculatorAdapterInterface,
        event_publisher: DomainEventPublisher,
    ):
        raise NotImplementedError

    @abc.abstractmethod
    async def create_new_order(
        self, order_id: OrderId, buyer_id: BuyerId, items: list[OrderItem], destination: Address
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def pay_order(self, order_id: OrderId):
        raise NotImplementedError

    @abc.abstractmethod
    async def cancel_order(self, order_id: OrderId):
        raise NotImplementedError

    @abc.abstractmethod
    async def _pay_order_tnx(self, order_id, is_payment_verified):
        raise NotImplementedError
