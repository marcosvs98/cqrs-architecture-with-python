import uuid
from enum import Enum

from bson import ObjectId
from pydantic import ConfigDict

from domain.base.dto import DataTransferObject
from domain.order.model.entities import Order
from domain.order.model.value_objects import BuyerId, OrderId, OrderItem
from domain.payment.model.value_objects import PaymentId


class Address(DataTransferObject):
    house_number: str
    road: str
    sub_district: str
    district: str
    state: str
    postcode: str
    country: str

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'house_number': '70',
                'road': 'Rua Afonso Charlier',
                'sub_district': 'SUB_DISTRICT',
                'district': 'Porto Alegre',
                'state': 'RS',
                'postcode': '92310010',
                'country': 'Brazil',
            }
        }
    )


class OrderCreateRequest(DataTransferObject):
    buyer_id: BuyerId
    items: list[OrderItem]
    destination: Address

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            'example': {
                'buyer_id': str(ObjectId()),
                'items': [{'product_id': '63ce91dc6a4c8287bfdde046', 'amount': 200}],
                'destination': Address.schema()['example'],
            }
        },
    )


class OrderCreateResponse(DataTransferObject):
    order_id: OrderId

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'order_id': str(ObjectId()),
            }
        }
    )


class OrderStatus(str, Enum):
    waiting: str = 'waiting'
    paid: str = 'paid'
    cancelled: str = 'cancelled'


class OrderUpdateStatusRequest(DataTransferObject):
    status: str

    model_config = ConfigDict(json_schema_extra={'example': {'status': 'paid'}})


class OrderUpdateStatusResponse(DataTransferObject):
    order_id: OrderId
    status: OrderStatus

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'order_id': str(ObjectId()),
                'status': 'paid',
            }
        }
    )

    @classmethod
    def from_order_id(cls, order_id: OrderId):
        return cls(order_id=str(order_id))


class OrderDetail(DataTransferObject):
    buyer_id: BuyerId
    payment_id: PaymentId
    items: list[OrderItem]
    product_cost: float
    delivery_cost: float
    total_cost: float
    status: OrderStatus

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'buyer_id': str(ObjectId()),
                'payment_id': str(uuid.uuid4()),
                'items': [{'product_id': '63ce91dc6a4c8287bfdde046', 'amount': 200}],
                'product_cost': 424.2,
                'delivery_cost': 42.42,
                'total_cost': 466.62,
                'status': 'waiting',
            }
        }
    )

    @classmethod
    def from_order(cls, order: Order):
        return cls(**order.dict(), total_cost=order.total_cost)
