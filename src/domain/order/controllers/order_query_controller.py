from typing import Annotated

from fastapi import APIRouter, Query, Request

from domain.order.dtos.order_dtos import OrderDetail, OrderListResponse
from domain.order.model.value_objects import BuyerId, OrderId, OrderStatusEnum
from domain.order.services.order_query_service import OrderQueryService


class OrderQueryController:
    """HTTP controller exposing read-side order endpoints."""

    def __init__(self, order_query_service: OrderQueryService) -> None:
        self.order_query_service = order_query_service
        self.router = APIRouter(tags=['Order Query'], prefix='/core/v1/orders')
        self.router.add_api_route(
            '/',
            self.list_orders,
            methods=['GET'],
            response_model=OrderListResponse,
        )
        self.router.add_api_route(
            '/{order_id}',
            self.get_order,
            methods=['GET'],
            response_model=OrderDetail,
        )

    async def get_order(self, request: Request, order_id: Annotated[str, OrderId]) -> OrderDetail:
        projection = await self.order_query_service.get_order(order_id=order_id)
        return OrderDetail.from_projection(projection)

    async def list_orders(
        self,
        request: Request,
        status: OrderStatusEnum | None = Query(default=None),
        buyer_id: Annotated[str | None, BuyerId] = Query(default=None),
        limit: int = Query(default=20, ge=1, le=200),
        offset: int = Query(default=0, ge=0),
    ) -> OrderListResponse:
        projections, total = await self.order_query_service.list_orders(
            buyer_id=buyer_id,
            status=status,
            limit=limit,
            offset=offset,
        )
        return OrderListResponse.from_projections(projections, total)
