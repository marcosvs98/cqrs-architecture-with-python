import uuid
from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal

from bson import ObjectId
from pydantic import ConfigDict, Field, computed_field

from domain.base.dto import DataTransferObject
from domain.maps.model.value_objects import Address as AddressValueObject
from domain.order.model.entities import Order
from domain.order.model.value_objects import BuyerId, OrderId, OrderItem, OrderStatusEnum
from domain.order.read_models.order_read_model import OrderReadModel
from domain.payment.model.value_objects import PaymentId


class OrderDestination(DataTransferObject):
    """Postal address DTO."""

    house_number: str | int | None
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
                'road': 'Rua Padre Emilio Hartmann',
                'sub_district': 'Hípica',
                'district': 'Porto Alegre',
                'state': 'RS',
                'postcode': '91755720',
                'country': 'Brazil',
            }
        }
    )

    def to_value_object(self) -> AddressValueObject:
        """Convert DTO to Address value object."""
        return AddressValueObject(
            house_number=self.house_number,
            road=self.road,
            sub_district=self.sub_district,
            district=self.district,
            state=self.state,
            postcode=self.postcode,
            country=self.country,
        )


class OrderCreateRequest(DataTransferObject):
    """Create-order request payload."""

    buyer_id: BuyerId
    items: Sequence[OrderItem]
    destination: OrderDestination

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            'example': {
                'buyer_id': str(ObjectId()),
                'items': [{'product_id': uuid.uuid4().hex, 'amount': 200}],
                'destination': OrderDestination.model_json_schema()['example'],
            }
        },
    )

    def to_value_object(self) -> AddressValueObject:
        """Convert DTO representation into domain value object."""
        return AddressValueObject.model_validate(self.model_dump())


class OrderCreateResponse(DataTransferObject):
    """Create-order response payload."""

    order_id: OrderId

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'order_id': str(ObjectId()),
            }
        }
    )


class OrderUpdateStatusRequest(DataTransferObject):
    """Update-order-status request payload."""

    status: OrderStatusEnum

    model_config = ConfigDict(json_schema_extra={'example': {'status': OrderStatusEnum.CANCELLED}})


class OrderUpdateStatusResponse(DataTransferObject):
    """Update-order-status response payload."""

    order_id: OrderId
    status: OrderStatusEnum

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'order_id': str(ObjectId()),
                'status': OrderStatusEnum.PAID,
            }
        }
    )

    @classmethod
    def from_order_id(cls, order_id: OrderId) -> 'OrderUpdateStatusResponse':
        """Factory from identifier."""
        return cls(order_id=order_id)


class OrderDetail(DataTransferObject):
    """Order detail view."""

    order_id: OrderId = Field(validation_alias='id')
    buyer_id: BuyerId
    payment_id: PaymentId
    items: Sequence[OrderItem]
    product_cost: Decimal
    delivery_cost: Decimal
    status: OrderStatusEnum

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'order_id': str(ObjectId()),
                'buyer_id': str(ObjectId()),
                'payment_id': uuid.uuid4().hex,
                'items': [{'product_id': uuid.uuid4().hex, 'amount': 200}],
                'product_cost': '424.20',
                'delivery_cost': '42.42',
                'total_cost': '466.62',
                'status': OrderStatusEnum.WAITING,
            }
        }
    )

    @computed_field  # type: ignore[misc]
    @property
    def total_cost(self) -> Decimal:
        """Computed total (products + delivery)."""
        return self.product_cost + self.delivery_cost

    @classmethod
    def from_order(cls, order: Order) -> 'OrderDetail':
        """Factory from aggregate."""
        return cls.model_validate(order.model_dump(mode='json'))

    @classmethod
    def from_projection(cls, projection: OrderReadModel) -> 'OrderDetail':
        """Build response payload from read-model projection."""
        return cls.model_validate(
            {
                'id': projection.order_id,
                'order_id': projection.order_id,
                'buyer_id': projection.buyer_id,
                'payment_id': projection.payment_id,
                'items': projection.items,
                'product_cost': projection.product_cost,
                'delivery_cost': projection.delivery_cost,
                'status': projection.status,
            }
        )


class OrderSummary(DataTransferObject):
    """Compact representation of order projections for listing endpoints."""

    order_id: OrderId
    buyer_id: BuyerId
    status: OrderStatusEnum
    total_cost: Decimal
    updated_at: datetime

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'order_id': str(ObjectId()),
                'buyer_id': str(ObjectId()),
                'status': OrderStatusEnum.WAITING,
                'total_cost': '120.00',
                'updated_at': datetime.utcnow().isoformat(),
            }
        }
    )

    @classmethod
    def from_projection(cls, projection: OrderReadModel) -> 'OrderSummary':
        return cls.model_validate(
            {
                'order_id': projection.order_id,
                'buyer_id': projection.buyer_id,
                'status': projection.status,
                'total_cost': projection.total_cost,
                'updated_at': projection.updated_at,
            }
        )


class OrderListResponse(DataTransferObject):
    """Paginated order listing payload."""

    count: int
    items: list[OrderSummary]

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'count': 1,
                'items': [
                    OrderSummary.model_validate(
                        {
                            'order_id': str(ObjectId()),
                            'buyer_id': str(ObjectId()),
                            'status': OrderStatusEnum.WAITING,
                            'total_cost': '120.00',
                            'updated_at': datetime.utcnow().isoformat(),
                        }
                    ).model_dump(mode='json')
                ],
            }
        }
    )

    @classmethod
    def from_projections(
        cls, projections: Sequence[OrderReadModel], total: int
    ) -> 'OrderListResponse':
        summaries = [OrderSummary.from_projection(projection) for projection in projections]
        return cls(count=total, items=summaries)
