from database import get_mongo_db
from settings import MongoDatabaseSettings
from typing import List
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from domain.order.ports.order_database_interface import OrderDatabaseInterface  # noqa: E501
from domain.order.value_objects import OrderId
from domain.order.entities import Order
from domain.order.exceptions.order_exceptions import EntityOutdated


class OrderDatabaseRepository(OrderDatabaseInterface):
    def __init__(self, collection_name='order'):
        self.db = get_mongo_db(MongoDatabaseSettings())
        self.collection_name = collection_name

    async def next_identity(self) -> OrderId:
        return OrderId(str(ObjectId()))

    async def all(self, limit=10) -> List[Order]:
        raw_list = await self.db[self.collection_name].find().to_list(limit)
        return [Order.deserialize(raw) for raw in raw_list]

    async def from_id(self, order_id: OrderId) -> Order:
        raw = await self.db[self.collection_name].find_one({'_id': ObjectId(str(order_id))})
        del raw['_id']
        return Order(**raw)

    async def save(self, entity: Order):
        data = entity.dict()
        order_id = ObjectId(str(entity.order_id))

        spec = {'_id': order_id, 'version': entity.version}
        update = {'$set': data, '$inc': {'version': 1}}
        del data['version']

        try:
            await self.db[self.collection_name].update_one(spec, update, upsert=True)
        except DuplicateKeyError as e:
            raise EntityOutdated(detail=f'Order with OrderId {order_id} is not dated') from e
