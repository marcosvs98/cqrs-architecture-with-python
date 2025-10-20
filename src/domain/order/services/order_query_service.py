from __future__ import annotations

from typing import Annotated

from domain.order.exceptions.order_exceptions import OrderNotFound
from domain.order.model.entities import Order
from domain.order.model.value_objects import BuyerId, OrderId, OrderStatusEnum
from domain.order.ports.order_event_store_repository_interface import (
    OrderEventStoreRepositoryInterface,
)
from domain.order.read_models.order_read_model import OrderReadModel
from domain.order.repositories.order_read_repository import OrderReadRepository
from utils.logger import get_logger

logger = get_logger()


class OrderQueryService:
    """Application service dedicated to query-side operations for orders."""

    def __init__(
        self,
        read_repository: OrderReadRepository,
        event_store: OrderEventStoreRepositoryInterface,
    ) -> None:
        self.read_repository = read_repository
        self.event_store = event_store

    async def get_order(self, order_id: Annotated[str, OrderId]) -> OrderReadModel:
        projection = await self.read_repository.from_id(order_id)
        if not projection:
            projection = await self._rebuild_projection(order_id)
            if not projection:
                await logger.warning('Order (read) not found', order_id=str(order_id))
                raise OrderNotFound(detail=f"order '{order_id}' not found")
        await logger.info('Order projection retrieved', order_id=str(order_id))
        return projection

    async def list_orders(
        self,
        *,
        buyer_id: Annotated[str | None, BuyerId] = None,
        status: OrderStatusEnum | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[OrderReadModel], int]:
        buyer = BuyerId(buyer_id) if buyer_id else None
        projections, total = await self.read_repository.list_with_count(
            buyer_id=buyer, status=status, limit=limit, offset=offset
        )
        await logger.info(
            'Order projections listed',
            filters={
                'buyer_id': str(buyer) if buyer else None,
                'status': str(status) if status else None,
            },
            limit=limit,
            offset=offset,
            total=total,
        )
        return projections, total

    async def _rebuild_projection(self, order_id: Annotated[str, OrderId]) -> OrderReadModel | None:
        last_event = await self.event_store.get_last_event_version_from_entity(order_id)
        if not last_event:
            return None
        order = await self.event_store.rebuild_aggregate_root(last_event, Order)
        await self.read_repository.project(order, last_event)
        projection = await self.read_repository.from_id(order_id)
        if projection:
            await logger.info('Order projection rebuilt from event store', order_id=str(order_id))
        return projection
