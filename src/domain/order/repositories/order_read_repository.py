from __future__ import annotations

from collections.abc import Sequence

from domain.base.event import DomainEvent
from domain.order.model.entities import Order
from domain.order.model.value_objects import BuyerId, OrderId, OrderStatusEnum
from domain.order.read_models.order_read_model import OrderReadModel
from ports.cache_interface import CacheInterface
from utils.logger import get_logger

logger = get_logger()


class OrderReadRepository:
    """Read-model repository supporting query-side projections of orders."""

    def __init__(
        self,
        cache_adapter: CacheInterface,
        db_connection,
        collection_name: str,
    ) -> None:
        self.cache_adapter = cache_adapter
        self.db_connection = db_connection
        self.collection_name = collection_name

    async def project(self, order: Order, event: DomainEvent) -> None:
        """Upsert the projection for the given aggregate based on a domain event."""
        projection = OrderReadModel.from_order(order, event)
        document = projection.model_dump(mode='json', by_alias=True)
        document['updated_at'] = event.datetime.isoformat()
        cache_key = self._cache_key(order.id)

        async with self.db_connection.get_connection() as connection:
            await connection[self.collection_name].replace_one(
                {'_id': document['_id']},
                document,
                upsert=True,
            )

        await self.cache_adapter.set(cache_key, data=document, ttl=300)

    async def from_id(self, order_id: OrderId) -> OrderReadModel | None:
        """Fetch projection by identifier."""
        cache_key = self._cache_key(order_id)

        if cached := await self.cache_adapter.get(cache_key):
            return OrderReadModel.model_validate(cached)

        async with self.db_connection.get_connection() as connection:
            document = await connection[self.collection_name].find_one({'_id': str(order_id)})
            if not document:
                return None
            await self.cache_adapter.set(cache_key, data=document, ttl=300)
            return OrderReadModel.model_validate(document)

    async def list_with_count(
        self,
        *,
        buyer_id: BuyerId | None = None,
        status: OrderStatusEnum | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[OrderReadModel], int]:
        """Return projections matching filters with total count."""
        criteria: dict[str, str] = {}
        if buyer_id:
            criteria['buyer_id'] = str(buyer_id)
        if status:
            criteria['status'] = status.value

        async with self.db_connection.get_connection() as connection:
            collection = connection[self.collection_name]
            cursor = collection.find(criteria).sort('updated_at', -1).skip(offset).limit(limit)
            documents: Sequence[dict] = await cursor.to_list(length=limit)
            total = await collection.count_documents(criteria)

        projections = [OrderReadModel.model_validate(doc) for doc in documents]
        return projections, total

    def _cache_key(self, order_id: OrderId | str) -> str:
        return f'order-read:{order_id}'
