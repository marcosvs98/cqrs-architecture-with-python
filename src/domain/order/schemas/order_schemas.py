import uuid
from typing import List
from enum import Enum
from bson import ObjectId
from pydantic import BaseModel
from domain.order.entities import Order
from domain.order.value_objects import OrderId
from domain.order.value_objects import BuyerId
from domain.payment.value_objects import PaymentId


class Address(BaseModel):
    house_number: str
    road: str
    sub_district: str
    district: str
    state: str
    postcode: str
    country: str

    class Config:
        schema_extra = {
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


class OrderItem(BaseModel):
    product_id: str
    amount: int

    class Config:
        schema_extra = {
            'example': {
                'product_id': str(ObjectId()),
                'amount': 20,
            }
        }


class OrderCreateRequest(BaseModel):
    buyer_id: BuyerId
    items: List[OrderItem]
    destination: Address

    class Config:
        schema_extra = {
            'example': {
                'buyer_id': str(ObjectId()),
                'items': [OrderItem.schema()['example']],
                'destination': Address.schema()['example'],
            }
        }


class OrderCreateResponse(BaseModel):
    order_id: OrderId

    class Config:
        schema_extra = {
            'example': {
                'order_id': str(ObjectId()),
            }
        }


class OrderStatus(str, Enum):
    waiting: str = 'waiting'
    paid: str = 'paid'
    cancelled: str = 'cancelled'


class OrderUpdateStatusRequest(BaseModel):
    status: str

    class Config:
        schema_extra = {'example': {'status': 'paid'}}


class OrderUpdateStatusResponse(BaseModel):
    order_id: OrderId
    status: OrderStatus

    class Config:
        schema_extra = {
            'example': {
                'order_id': str(ObjectId()),
                'status': 'paid',
            }
        }

    @classmethod
    def from_order_id(cls, order_id: OrderId):
        return cls(order_id=str(order_id))


class OrderDetail(BaseModel):
    buyer_id: BuyerId
    payment_id: PaymentId
    items: List[OrderItem]

    product_cost: float
    delivery_cost: float
    total_cost: float
    status: OrderStatus

    class Config:
        schema_extra = {
            'example': {
                'buyer_id': str(ObjectId()),
                'payment_id': str(uuid.uuid4()),
                'items': [OrderItem.schema()['example']],
                'product_cost': 424.2,
                'delivery_cost': 42.42,
                'total_cost': 466.62,
                'status': 'waiting',
            }
        }

    @classmethod
    def from_order(cls, order: Order):
        return cls(**order.dict(), total_cost=order.total_cost)
