from fastapi import APIRouter, HTTPException, Request
from domain.order.ports.order_service_interface import OrderServiceInterface

from domain.order.value_objects import BuyerId
from domain.order.value_objects import OrderId


from domain.order.exceptions.order_exceptions import (
    OrderAlreadyPaidException,
    OrderAlreadyCancelledException,
    PaymentNotVerifiedException,
)


from domain.order.schemas.order_schemas import (
    OrderCreateRequest,
    OrderCreateResponse,
    OrderDetail,
    OrderUpdateStatusRequest,
    OrderStatus,
    OrderUpdateStatusResponse,
)


class OrderController:
    def __init__(self, order_service: OrderServiceInterface):
        self.service = order_service
        self.router = APIRouter()
        self.router.add_api_route(
            '/', self.create_order, methods=['POST'], response_model=OrderCreateResponse
        )  # noqa: E501
        self.router.add_api_route(
            '/{order_id}', self.get_order, methods=['GET'], response_model=OrderDetail
        )  # noqa: F541
        self.router.add_api_route(
            '/{order_id}',
            self.update_order,
            methods=['PATCH'],
            response_model=OrderUpdateStatusResponse,
        )  # noqa: F541

    async def create_order(self, request: Request, order: OrderCreateRequest):
        buyer_id = BuyerId(order.buyer_id)
        order_id = await self.service.create_new_order(buyer_id, order.items, order.destination)
        return OrderCreateResponse(order_id=str(order_id))

    async def get_order(self, request: Request, order_id):
        order = await self.service.get_order_from_id(order_id=order_id)
        return OrderDetail.from_order(order)

    async def update_order(
        self, request: Request, order_id, order_status: OrderUpdateStatusRequest
    ):
        order_id = OrderId(order_id)

        if order_status.status == OrderStatus.paid:
            await self._pay_order(order_id)
            order = OrderUpdateStatusResponse(order_id=str(order_id), status='paid')
        elif order_status.status == OrderStatus.cancelled:
            await self._cancel_order(order_id)
            order = OrderUpdateStatusResponse(order_id=str(order_id), status='cancelled')
        else:
            error_detail = f"Cannot update Order's status to {order_status.status}"
            raise HTTPException(status_code=403, detail=error_detail)
        return order

    async def _pay_order(self, order_id: OrderId):
        try:
            return await self.service.pay_order(order_id)
        except OrderAlreadyCancelledException as e:
            error_detail = "Cannot pay for Order when it's already cancelled"
            raise HTTPException(status_code=409, detail=error_detail) from e
        except OrderAlreadyPaidException as e:
            error_detail = "Cannot pay for Order when it's already paid"
            raise HTTPException(status_code=409, detail=error_detail) from e
        except PaymentNotVerifiedException as e:
            error_detail = 'Payment verification failed'
            raise HTTPException(status_code=403, detail=error_detail) from e

    async def _cancel_order(self, order_id: OrderId):
        try:
            return await self.service.cancel_order(order_id)
        except OrderAlreadyCancelledException as e:
            error_detail = "Cannot cancel Order when it's already cancelled"
            raise HTTPException(status_code=409, detail=error_detail) from e
        except OrderAlreadyPaidException as e:
            error_detail = "Cannot cancel Order when it's already paid"
            raise HTTPException(status_code=409, detail=error_detail) from e
