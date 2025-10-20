from typing import Annotated

from fastapi import APIRouter, Request

from domain.order.dtos.order_dtos import (
    OrderCreateRequest,
    OrderCreateResponse,
    OrderStatusEnum,
    OrderUpdateStatusRequest,
    OrderUpdateStatusResponse,
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
from domain.order.model.value_objects import BuyerId, OrderId
from domain.order.ports.order_service_interface import OrderServiceInterface


class OrderController:
    """HTTP controller for Order resource."""

    def __init__(self, order_service: OrderServiceInterface) -> None:
        """Bind routes and dependencies."""
        self.order_service = order_service
        self.router = APIRouter(tags=['Order Command'], prefix='/core/v1/orders')
        self.router.add_api_route(
            '/', self.create_order, methods=['POST'], response_model=OrderCreateResponse
        )
        self.router.add_api_route(
            '/{order_id}',
            self.update_order,
            methods=['PATCH'],
            response_model=OrderUpdateStatusResponse,
        )

    async def create_order(
        self, request: Request, order: OrderCreateRequest
    ) -> OrderCreateResponse:
        """Create a new order."""
        buyer_id = BuyerId(order.buyer_id)
        destination = order.destination.to_value_object()
        order_id = await self.order_service.create_new_order(
            buyer_id, list(order.items), destination
        )
        return OrderCreateResponse(order_id=str(order_id))

    async def update_order(
        self,
        request: Request,
        order_id: Annotated[str, OrderId],
        order_update: OrderUpdateStatusRequest,
    ) -> OrderUpdateStatusResponse:
        """Update order status."""
        if not order_id or not str(order_id).strip():
            raise OrderIdRequired(errors=['blank'])

        order_status = order_update.status

        if order_status is OrderStatusEnum.PAID:
            await self._pay_order(order_id)
            return OrderUpdateStatusResponse(order_id=str(order_id), status='paid')

        if order_status is OrderStatusEnum.CANCELLED:
            await self._cancel_order(order_id)
            return OrderUpdateStatusResponse(order_id=str(order_id), status='cancelled')

        raise CannotUpdateToStatus(detail=f"Cannot update Order's status to {order_status}")

    async def _pay_order(self, order_id: Annotated[str, OrderId]) -> None:
        """Apply payment transition."""
        try:
            await self.order_service.pay_order(order_id)
        except OrderAlreadyCancelledException as e:
            raise CannotPayCancelled() from e
        except OrderAlreadyPaidException as e:
            raise CannotPayAlreadyPaid() from e
        except PaymentNotVerifiedException as e:
            raise PaymentVerificationFailed() from e

    async def _cancel_order(self, order_id: OrderId) -> None:
        """Apply cancel transition."""
        try:
            await self.order_service.cancel_order(order_id)
        except OrderAlreadyCancelledException as e:
            raise CannotCancelAlreadyCancelled() from e
        except OrderAlreadyPaidException as e:
            raise CannotCancelAlreadyPaid() from e
