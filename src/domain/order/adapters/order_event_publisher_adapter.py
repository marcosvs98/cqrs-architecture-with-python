from database import get_mongo_db
from settings import MongoDatabaseSettings
from domain.base.event import DomainEvent
from domain.base.ports.event_adapter_interface import DomainEventPublisher


class OrderEventPublisher(DomainEventPublisher):
    def __init__(self, collection_name='order_events'):
        self.event_source = get_mongo_db(MongoDatabaseSettings())
        self.collection_name = collection_name

    async def publish(self, event: DomainEvent):
        await self.event_source[self.collection_name].insert_one(event.dict())
