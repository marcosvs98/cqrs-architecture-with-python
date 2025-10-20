# pylint: disable=redefined-outer-name
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from domain.base.ports.event_adapter_interface import DomainEventPublisher
from domain.delivery.ports.cost_calculator_interface import DeliveryCostCalculatorAdapterInterface
from domain.order.exceptions.order_exceptions import (
    OrderAlreadyPaidException,
    OrderNotFound,
    PaymentNotVerifiedException,
)
from domain.order.model.entities import Order
from domain.order.model.value_objects import BuyerId, OrderId, OrderItem, OrderStatusEnum
from domain.order.ports.order_event_store_repository_interface import (
    OrderEventStoreRepositoryInterface,
)
from domain.order.ports.order_repository_interface import OrderRepositoryInterface
from domain.order.repositories.order_read_repository import OrderReadRepository
from domain.order.services.order_service import OrderService
from domain.payment.model.value_objects import PaymentId
from domain.payment.ports.payment_adapter_interface import PaymentAdapterInterface
from domain.product.ports.product_adapter_interface import ProductAdapterInterface


@pytest.fixture
def service_with_deps():
    repository = AsyncMock(spec=OrderRepositoryInterface)
    event_store = AsyncMock(spec=OrderEventStoreRepositoryInterface)
    read_repository = AsyncMock(spec=OrderReadRepository)
    payment_service = AsyncMock(spec=PaymentAdapterInterface)
    product_service = AsyncMock(spec=ProductAdapterInterface)
    delivery_service = AsyncMock(spec=DeliveryCostCalculatorAdapterInterface)
    event_publisher = AsyncMock(spec=DomainEventPublisher)

    product_service.total_price.return_value = Decimal('120.50')
    payment_service.new_payment.return_value = PaymentId('payment-1')
    delivery_service.calculate_cost.return_value = Decimal('30.00')

    service = OrderService(
        repository=repository,
        payment_service=payment_service,
        product_service=product_service,
        delivery_service=delivery_service,
        event_store=event_store,
        read_repository=read_repository,
        event_publisher=event_publisher,
    )

    deps = SimpleNamespace(
        repository=repository,
        event_store=event_store,
        read_repository=read_repository,
        payment_service=payment_service,
        product_service=product_service,
        delivery_service=delivery_service,
        event_publisher=event_publisher,
    )

    return service, deps


@pytest.mark.asyncio
async def test_create_new_order_projects_and_publishes(service_with_deps):
    service, deps = service_with_deps
    order_id = await service.create_new_order(
        buyer_id=BuyerId('buyer-1'),
        items=[OrderItem(product_id='product-1', amount=Decimal('2'))],
        destination=SimpleNamespace(),
    )

    saved_order = deps.repository.save.await_args.args[0]
    assert isinstance(order_id, OrderId)
    assert saved_order.product_cost == Decimal('120.50')
    assert saved_order.delivery_cost == Decimal('30.00')
    deps.event_store.save.assert_awaited()
    deps.read_repository.project.assert_awaited()
    deps.event_publisher.publish.assert_awaited()


@pytest.mark.asyncio
async def test_pay_order_success(service_with_deps):
    service, deps = service_with_deps
    order = Order(
        buyer_id=BuyerId('buyer-1'),
        items=[OrderItem(product_id='product-1', amount=Decimal('1'))],
        product_cost=Decimal('10.00'),
        delivery_cost=Decimal('5.00'),
        payment_id=PaymentId('payment-1'),
    )
    deps.repository.from_id.return_value = order
    deps.payment_service.verify_payment.return_value = True

    await service.pay_order(OrderId(order.id))

    assert order.is_paid()
    deps.repository.save.assert_awaited_with(order)
    deps.event_store.save.assert_awaited()
    deps.read_repository.project.assert_awaited()
    deps.event_publisher.publish.assert_awaited()


@pytest.mark.asyncio
async def test_pay_order_payment_rejected(service_with_deps):
    service, deps = service_with_deps
    order = Order(
        buyer_id=BuyerId('buyer-1'),
        items=[OrderItem(product_id='product-1', amount=Decimal('1'))],
        product_cost=Decimal('10.00'),
        delivery_cost=Decimal('5.00'),
        payment_id=PaymentId('payment-1'),
    )
    deps.repository.from_id.return_value = order
    deps.payment_service.verify_payment.return_value = False

    with pytest.raises(PaymentNotVerifiedException):
        await service.pay_order(OrderId(order.id))

    assert order.status is OrderStatusEnum.PAYMENT_REJECTED
    deps.event_store.save.assert_awaited()
    deps.read_repository.project.assert_awaited()
    deps.event_publisher.publish.assert_awaited()


@pytest.mark.asyncio
async def test_cancel_order_rejects_when_paid(service_with_deps):
    service, deps = service_with_deps
    order = Order(
        buyer_id=BuyerId('buyer-1'),
        items=[OrderItem(product_id='product-1', amount=Decimal('1'))],
        product_cost=Decimal('10.00'),
        delivery_cost=Decimal('5.00'),
        payment_id=PaymentId('payment-1'),
        status=OrderStatusEnum.PAID,
    )
    deps.repository.from_id.return_value = order

    with pytest.raises(OrderAlreadyPaidException):
        await service.cancel_order(OrderId(order.id))

    assert order.status is OrderStatusEnum.CANCELLATION_REJECTED
    deps.event_store.save.assert_awaited()
    deps.read_repository.project.assert_awaited()
    deps.event_publisher.publish.assert_awaited()


@pytest.mark.asyncio
async def test_cancel_order_success(service_with_deps):
    service, deps = service_with_deps
    order = Order(
        buyer_id=BuyerId('buyer-1'),
        items=[OrderItem(product_id='product-1', amount=Decimal('1'))],
        product_cost=Decimal('10.00'),
        delivery_cost=Decimal('5.00'),
        payment_id=PaymentId('payment-1'),
    )
    deps.repository.from_id.return_value = order

    await service.cancel_order(OrderId(order.id))

    assert order.status is OrderStatusEnum.CANCELLED
    deps.repository.save.assert_awaited_with(order)
    deps.event_store.save.assert_awaited()
    deps.read_repository.project.assert_awaited()
    deps.event_publisher.publish.assert_awaited()


@pytest.mark.asyncio
async def test_get_order_not_found(service_with_deps):
    service, deps = service_with_deps
    deps.repository.from_id.return_value = None

    with pytest.raises(OrderNotFound):
        await service.get_order_from_id(OrderId('order-404'))
