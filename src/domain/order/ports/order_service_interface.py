import abc
from typing import List

from domain.order.value_objects import BuyerId, OrderItem, OrderId
from domain.order.entities import Order
from domain.maps.value_objects import Address

from domain.order.ports.order_database_interface import OrderDatabaseInterface  # noqa: E501
from domain.payment.ports.payment_adapter_interface import PaymentAdapterInterface  # noqa: E501
from domain.product.ports.product_adapter_interface import ProductAdapterInterface  # noqa: E501
from domain.delivery.ports.cost_calculator_interface import (
    DeliveryCostCalculatorAdapterInterface,
)  # noqa: E501
from domain.base.ports.event_adapter_interface import DomainEventPublisher  # noqa: E501


class OrderServiceInterface(abc.ABC):

    repository: OrderDatabaseInterface

    @abc.abstractmethod
    def __init__(
        self,
        repository: OrderDatabaseInterface,
        payment_service: PaymentAdapterInterface,
        product_service: ProductAdapterInterface,
        delivery_service: DeliveryCostCalculatorAdapterInterface,
        event_publisher: DomainEventPublisher,
    ):
        raise NotImplementedError

    @abc.abstractmethod
    async def create_new_order(
        self, buyer_id: BuyerId, items: List[OrderItem], destination: Address
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

    @abc.abstractmethod
    async def _pay_order_tnx(self, order_id, is_payment_verified):
        raise NotImplementedError
