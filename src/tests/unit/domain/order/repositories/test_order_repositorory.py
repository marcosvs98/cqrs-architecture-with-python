# pylint: disable=redefined-outer-name
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio

from adapters.redis_adapter import RedisAdapter
from domain.order.exceptions.order_exceptions import EntityOutdated, PersistenceError
from domain.order.model.entities import Order
from domain.order.repositories.order_repository import OrderRepository


@pytest_asyncio.fixture
def order_repository():
    collection = AsyncMock()

    connection_cm = AsyncMock()
    connection_cm.__aenter__.return_value = {'orders': collection}
    connection_cm.__aexit__.return_value = None

    db_connection = MagicMock()
    db_connection.get_connection.return_value = connection_cm

    repository = OrderRepository(
        cache_adapter=AsyncMock(spec=RedisAdapter),
        db_connection=db_connection,
        collection_name='orders',
    )
    return repository


@pytest.mark.asyncio
async def test_from_id_returns_from_cache(order_repository):
    repo = order_repository
    cache = repo.cache_adapter
    order = Order(buyer_id='b1', items=[], product_cost=10.0, delivery_cost=5.0, payment_id='p1')
    cache.get.return_value = order.model_dump(mode='json')
    result = await repo.from_id(order.id)
    assert isinstance(result, Order)
    assert result.id == order.id


@pytest.mark.asyncio
async def test_from_id_fetches_from_db_and_sets_cache(order_repository):
    repo = order_repository
    cache = repo.cache_adapter
    collection = repo.db_connection.get_connection.return_value.__aenter__.return_value['orders']
    cache.get.return_value = None
    order = Order(buyer_id='b2', items=[], product_cost=20.0, delivery_cost=10.0, payment_id='p2')
    collection.find_one.return_value = order.model_dump(mode='json')
    result = await repo.from_id(order.id)
    assert isinstance(result, Order)
    assert result.id == order.id
    cache.set.assert_awaited_once_with(
        key=str(order.id), data=order.model_dump(mode='json'), ttl=300
    )


@pytest.mark.asyncio
async def test_from_id_returns_none_if_not_found(order_repository):
    repo = order_repository
    cache = repo.cache_adapter
    collection = repo.db_connection.get_connection.return_value.__aenter__.return_value['orders']
    cache.get.return_value = None
    collection.find_one.return_value = None
    result = await repo.from_id('missing-id')
    assert result is None


@pytest.mark.asyncio
async def test_save_inserts_new_order(order_repository):
    repo = order_repository
    cache = repo.cache_adapter
    collection = repo.db_connection.get_connection.return_value.__aenter__.return_value['orders']
    repo.from_id = AsyncMock(return_value=None)
    collection.replace_one.return_value = MagicMock()
    order = Order(buyer_id='b3', items=[], product_cost=15.0, delivery_cost=7.0, payment_id='p3')
    await repo.save(order)
    collection.replace_one.assert_awaited_once()
    cache.set.assert_awaited()


@pytest.mark.asyncio
async def test_save_updates_existing_order(order_repository):
    repo = order_repository
    collection = repo.db_connection.get_connection.return_value.__aenter__.return_value['orders']
    existing_order = Order(
        buyer_id='b4', items=[], product_cost=12.0, delivery_cost=6.0, payment_id='p4'
    )
    existing_order.version = 1
    repo.from_id = AsyncMock(return_value=existing_order)
    order = Order(buyer_id='b4', items=[], product_cost=12.0, delivery_cost=6.0, payment_id='p4')
    order.version = 1
    await repo.save(order)
    collection.replace_one.assert_awaited_once()
    assert order.version == 2


@pytest.mark.asyncio
async def test_save_raises_entity_outdated(order_repository):
    repo = order_repository
    existing_order = Order(
        buyer_id='b5', items=[], product_cost=30.0, delivery_cost=15.0, payment_id='p5'
    )
    existing_order.version = 5
    repo.from_id = AsyncMock(return_value=existing_order)
    order = Order(buyer_id='b5', items=[], product_cost=30.0, delivery_cost=15.0, payment_id='p5')
    order.version = 1
    with pytest.raises(EntityOutdated):
        await repo.save(order)


@pytest.mark.asyncio
async def test_save_raises_persistence_error(order_repository):
    repo = order_repository
    collection = repo.db_connection.get_connection.return_value.__aenter__.return_value['orders']
    repo.from_id = AsyncMock(return_value=None)
    order = Order(buyer_id='b6', items=[], product_cost=50.0, delivery_cost=25.0, payment_id='p6')
    collection.replace_one.side_effect = Exception('db failure')
    with pytest.raises(PersistenceError):
        await repo.save(order)


@pytest.mark.asyncio
async def test_delete(order_repository):
    repo = order_repository
    cache = repo.cache_adapter
    collection = repo.db_connection.get_connection.return_value.__aenter__.return_value['orders']
    await repo.delete('some-id')
    cache.delete.assert_awaited_once_with(key='some-id')
    collection.delete_one.assert_awaited_once_with({'_id': 'some-id'})
