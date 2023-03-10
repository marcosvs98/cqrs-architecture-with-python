from bson.objectid import ObjectId

from pymongo.errors import DuplicateKeyError
from adapters.database import get_event_store
from domain.order.ports.order_database_interface import OrderDatabaseInterface  # noqa: E501
from domain.order.value_objects import OrderId
from domain.order.entities import Order
from domain.order.exceptions.order_exceptions import EntityOutdated


class OrderDatabaseRepository(OrderDatabaseInterface):
    def __init__(self, collection_name='order'):
        self.event_store = get_event_store()
        self.collection_name = collection_name

    async def from_id(self, order_id: OrderId) -> Order:
        document = await self.event_store.get(index=self.collection_name, id=order_id)
        return Order(**document['_source'])

    async def save(self, entity: Order):
        body = entity.dict()
        order_id = ObjectId(str(entity.order_id))
        try:
            await self.event_store.index(index=self.collection_name, id=order_id, body=body)
        except DuplicateKeyError as e:
            raise EntityOutdated(detail=f'Order with OrderId {order_id} is not dated') from e
