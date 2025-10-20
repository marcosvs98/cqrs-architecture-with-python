# pylint: disable=redefined-outer-name, protected-access
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import Request
from pydantic import ValidationError

from domain.order.controllers.order_controller import OrderController
from domain.order.dtos.order_dtos import (
    OrderCreateRequest,
    OrderDestination,
    OrderUpdateStatusRequest,
)
from domain.order.exceptions.order_exceptions import (
    CannotCancelAlreadyCancelled,
    CannotCancelAlreadyPaid,
    CannotPayAlreadyPaid,
    CannotPayCancelled,
    CannotUpdateToStatus,
    OrderAlreadyCancelledException,
    OrderAlreadyPaidException,
    OrderIdRequired,
    PaymentNotVerifiedException,
    PaymentVerificationFailed,
)
from domain.order.model.value_objects import OrderId, OrderItem


@pytest.fixture
def order_service() -> SimpleNamespace:
    service = SimpleNamespace()
    service.create_new_order = AsyncMock()
    service.pay_order = AsyncMock()
    service.cancel_order = AsyncMock()
    return service


@pytest.fixture
def order_controller(order_service: SimpleNamespace) -> OrderController:
    return OrderController(order_service=order_service)


@pytest.mark.asyncio
async def test_create_order_success(
    order_controller: OrderController, order_service: SimpleNamespace
):
    order_service.create_new_order.return_value = OrderId('o1')
    req = Request(scope={'type': 'http'})
    order = OrderCreateRequest(
        buyer_id='b1',
        items=[OrderItem(product_id='p1', amount=1)],
        destination=OrderDestination(
            house_number='S/N',
            road='Rua A',
            sub_district='Bairro X',
            district='Cidade Y',
            state='RS',
            postcode='12345-678',
            country='Brasil',
        ),
    )
    response = await order_controller.create_order(req, order)
    assert response.order_id == 'o1'
    order_service.create_new_order.assert_awaited()


@pytest.mark.asyncio
async def test_update_order_blank_order_id(order_controller: OrderController):
    req = Request(scope={'type': 'http'})
    with pytest.raises(OrderIdRequired):
        await order_controller.update_order(req, '', OrderUpdateStatusRequest(status='paid'))


@pytest.mark.asyncio
async def test_update_order_blank_status(order_controller: OrderController):
    req = Request(scope={'type': 'http'})
    with pytest.raises(ValidationError):
        await order_controller.update_order(req, 'o1', OrderUpdateStatusRequest(status=''))


@pytest.mark.asyncio
async def test_update_order_invalid_status(order_controller: OrderController):
    req = Request(scope={'type': 'http'})
    with pytest.raises(ValidationError):
        await order_controller.update_order(req, 'o1', OrderUpdateStatusRequest(status='INVALID'))


@pytest.mark.asyncio
async def test_update_order_paid_success(order_controller: OrderController):
    order_controller._pay_order = AsyncMock()
    req = Request(scope={'type': 'http'})
    result = await order_controller.update_order(req, 'o1', OrderUpdateStatusRequest(status='paid'))
    assert result.status == 'paid'
    order_controller._pay_order.assert_awaited_with('o1')


@pytest.mark.asyncio
async def test_update_order_cancelled_success(order_controller: OrderController):
    order_controller._cancel_order = AsyncMock()
    req = Request(scope={'type': 'http'})
    result = await order_controller.update_order(
        req, 'o1', OrderUpdateStatusRequest(status='cancelled')
    )
    assert result.status == 'cancelled'
    order_controller._cancel_order.assert_awaited_with('o1')


@pytest.mark.asyncio
async def test_update_order_invalid_transition(order_controller: OrderController):
    req = Request(scope={'type': 'http'})
    with pytest.raises(CannotUpdateToStatus):
        await order_controller.update_order(req, 'o1', OrderUpdateStatusRequest(status='waiting'))


@pytest.mark.asyncio
async def test__pay_order_success(
    order_controller: OrderController, order_service: SimpleNamespace
):
    await order_controller._pay_order('o1')
    order_service.pay_order.assert_awaited_with('o1')


@pytest.mark.asyncio
async def test__pay_order_already_cancelled(
    order_controller: OrderController, order_service: SimpleNamespace
):
    order_service.pay_order.side_effect = OrderAlreadyCancelledException()
    with pytest.raises(CannotPayCancelled):
        await order_controller._pay_order('o1')


@pytest.mark.asyncio
async def test__pay_order_already_paid(
    order_controller: OrderController, order_service: SimpleNamespace
):
    order_service.pay_order.side_effect = OrderAlreadyPaidException()
    with pytest.raises(CannotPayAlreadyPaid):
        await order_controller._pay_order('o1')


@pytest.mark.asyncio
async def test__pay_order_not_verified(
    order_controller: OrderController, order_service: SimpleNamespace
):
    order_service.pay_order.side_effect = PaymentNotVerifiedException()
    with pytest.raises(PaymentVerificationFailed):
        await order_controller._pay_order('o1')


@pytest.mark.asyncio
async def test__cancel_order_success(
    order_controller: OrderController, order_service: SimpleNamespace
):
    await order_controller._cancel_order('o1')
    order_service.cancel_order.assert_awaited_with('o1')


@pytest.mark.asyncio
async def test__cancel_order_already_cancelled(
    order_controller: OrderController, order_service: SimpleNamespace
):
    order_service.cancel_order.side_effect = OrderAlreadyCancelledException()
    with pytest.raises(CannotCancelAlreadyCancelled):
        await order_controller._cancel_order('o1')


@pytest.mark.asyncio
async def test__cancel_order_already_paid(
    order_controller: OrderController, order_service: SimpleNamespace
):
    order_service.cancel_order.side_effect = OrderAlreadyPaidException()
    with pytest.raises(CannotCancelAlreadyPaid):
        await order_controller._cancel_order('o1')
