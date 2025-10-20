# pylint: disable=redefined-outer-name
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import Request

from domain.order.controllers.order_query_controller import OrderQueryController
from domain.order.dtos.order_dtos import OrderListResponse
from domain.order.read_models.order_read_model import OrderReadModel


@pytest.fixture
def order_query_service() -> SimpleNamespace:
    service = SimpleNamespace()
    service.get_order = AsyncMock()
    service.list_orders = AsyncMock()
    return service


@pytest.fixture
def controller(order_query_service: SimpleNamespace) -> OrderQueryController:
    return OrderQueryController(order_query_service=order_query_service)


@pytest.fixture
def projection() -> OrderReadModel:
    return OrderReadModel.model_validate(
        {
            '_id': 'order-1',
            'buyer_id': 'buyer-1',
            'payment_id': 'payment-1',
            'items': [{'product_id': 'product-1', 'amount': '1'}],
            'status': 'waiting',
            'product_cost': '10.00',
            'delivery_cost': '5.00',
            'total_cost': '15.00',
            'updated_at': datetime.utcnow().isoformat(),
        }
    )


@pytest.mark.asyncio
async def test_get_order_returns_projection(
    controller: OrderQueryController,
    order_query_service: SimpleNamespace,
    projection: OrderReadModel,
):
    order_query_service.get_order.return_value = projection
    request = Request(scope={'type': 'http'})

    response = await controller.get_order(request, projection.order_id)

    assert response.order_id == projection.order_id
    assert response.status == projection.status
    order_query_service.get_order.assert_awaited_with(order_id=projection.order_id)


@pytest.mark.asyncio
async def test_list_orders_returns_paginated_response(
    controller: OrderQueryController,
    order_query_service: SimpleNamespace,
    projection: OrderReadModel,
):
    order_query_service.list_orders.return_value = ([projection], 1)
    request = Request(scope={'type': 'http'})

    response = await controller.list_orders(request)

    assert isinstance(response, OrderListResponse)
    assert response.count == 1
    assert response.items[0].order_id == projection.order_id
    order_query_service.list_orders.assert_awaited()
