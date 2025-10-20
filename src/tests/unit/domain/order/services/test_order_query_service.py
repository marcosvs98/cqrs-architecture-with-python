# pylint: disable=redefined-outer-name
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from domain.order.exceptions.order_exceptions import OrderNotFound
from domain.order.model.entities import Order
from domain.order.model.events import OrderCreated
from domain.order.model.value_objects import BuyerId, OrderId, OrderItem
from domain.order.ports.order_event_store_repository_interface import (
    OrderEventStoreRepositoryInterface,
)
from domain.order.read_models.order_read_model import OrderReadModel
from domain.order.repositories.order_read_repository import OrderReadRepository
from domain.order.services.order_query_service import OrderQueryService


@pytest.fixture
def read_repository() -> AsyncMock:
    return AsyncMock(spec=OrderReadRepository)


@pytest.fixture
def event_store() -> AsyncMock:
    return AsyncMock(spec=OrderEventStoreRepositoryInterface)


@pytest.fixture
def service(read_repository, event_store) -> OrderQueryService:
    return OrderQueryService(read_repository=read_repository, event_store=event_store)


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
async def test_get_order_returns_projection(service, read_repository, projection):
    read_repository.from_id.return_value = projection

    result = await service.get_order(OrderId('order-1'))

    assert result.order_id == projection.order_id
    read_repository.from_id.assert_awaited_with(OrderId('order-1'))


@pytest.mark.asyncio
async def test_get_order_rebuilds_projection(service, read_repository, event_store, projection):
    order = Order(
        buyer_id=BuyerId('buyer-1'),
        items=[OrderItem(product_id='product-1', amount=Decimal('1'))],
        product_cost=Decimal('10.00'),
        delivery_cost=Decimal('5.00'),
        payment_id='payment-1',
    )
    event = OrderCreated(aggregate=order)
    read_repository.from_id.side_effect = [None, projection]
    event_store.get_last_event_version_from_entity.return_value = event
    event_store.rebuild_aggregate_root.return_value = order

    result = await service.get_order(OrderId(order.id))

    assert result.order_id == projection.order_id
    event_store.rebuild_aggregate_root.assert_awaited_with(event, Order)
    read_repository.project.assert_awaited_with(order, event)


@pytest.mark.asyncio
async def test_get_order_raises_when_missing(service, read_repository, event_store):
    read_repository.from_id.return_value = None
    event_store.get_last_event_version_from_entity.return_value = None

    with pytest.raises(OrderNotFound):
        await service.get_order(OrderId('order-missing'))


@pytest.mark.asyncio
async def test_list_orders(service, read_repository, projection):
    read_repository.list_with_count.return_value = ([projection], 1)

    projections, total = await service.list_orders(limit=5, offset=0)

    assert total == 1
    assert projections[0].order_id == projection.order_id
    read_repository.list_with_count.assert_awaited_with(
        buyer_id=None,
        status=None,
        limit=5,
        offset=0,
    )
