# pylint: disable=redefined-outer-name
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from domain.order.model.entities import Order
from domain.order.model.events import OrderCreated
from domain.order.model.value_objects import BuyerId, OrderId, OrderItem
from domain.order.repositories.order_read_repository import OrderReadRepository


class FakeConnectionManager:
    def __init__(self, connection):
        self.connection = connection

    async def __aenter__(self):
        return self.connection

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.fixture
def cache_adapter() -> SimpleNamespace:
    adapter = SimpleNamespace()
    adapter.get = AsyncMock(return_value=None)
    adapter.set = AsyncMock()
    adapter.delete = AsyncMock()
    return adapter


def make_connection(collection):
    conn = {}
    conn['order_read'] = collection
    return conn


@pytest.fixture
def repository(cache_adapter):
    db = SimpleNamespace()
    db.get_connection = lambda: FakeConnectionManager(make_connection(AsyncMock()))
    repo = OrderReadRepository(
        cache_adapter=cache_adapter, db_connection=db, collection_name='order_read'
    )
    return repo, db


def build_order() -> Order:
    return Order(
        buyer_id=BuyerId('buyer-1'),
        items=[OrderItem(product_id='product-1', amount=Decimal('1'))],
        product_cost=Decimal('10.00'),
        delivery_cost=Decimal('5.00'),
        payment_id='payment-1',
    )


@pytest.mark.asyncio
async def test_project_upserts_and_caches(repository, cache_adapter):
    repo, db = repository
    order = build_order()
    event = OrderCreated(aggregate=order)

    collection = AsyncMock()
    collection.replace_one = AsyncMock(return_value=None)
    db.get_connection = lambda: FakeConnectionManager(make_connection(collection))

    await repo.project(order, event)

    collection.replace_one.assert_awaited()
    # Ensure updated_at stored as ISO string
    stored_doc = collection.replace_one.await_args.args[1]
    assert stored_doc['_id'] == str(order.id)
    assert isinstance(stored_doc['updated_at'], str)
    cache_adapter.set.assert_awaited()
    assert cache_adapter.set.await_args.kwargs['ttl'] == 300


@pytest.mark.asyncio
async def test_from_id_hits_cache_first(repository, cache_adapter):
    repo, _ = repository
    projection = {
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
    cache_adapter.get.return_value = projection

    result = await repo.from_id(OrderId('order-1'))

    assert result.order_id == OrderId('order-1')
    cache_adapter.get.assert_awaited()


@pytest.mark.asyncio
async def test_list_with_count_returns_projections(repository, cache_adapter):
    repo, db = repository
    document = {
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

    class MockCursor:
        def __init__(self, document):
            self.document = document

        def sort(self, field, direction):
            return self

        def skip(self, offset):
            return self

        def limit(self, limit):
            return self

        async def to_list(self, length):
            return [self.document]

    cursor = MockCursor(document)
    collection = SimpleNamespace(
        find=lambda criteria: cursor, count_documents=AsyncMock(return_value=1)
    )
    db.get_connection = lambda: FakeConnectionManager(make_connection(collection))

    projections, total = await repo.list_with_count(limit=10, offset=0)

    assert total == 1
    assert len(projections) == 1
    assert projections[0].order_id == OrderId('order-1')
    collection.count_documents.assert_awaited()
