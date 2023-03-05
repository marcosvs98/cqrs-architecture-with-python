from adapters.database import get_event_store
from domain.base.event import DomainEvent
from domain.base.ports.event_adapter_interface import DomainEventPublisher


class OrderEventPublisher(DomainEventPublisher):
    def __init__(self, collection_name='order_events'):
        self.event_store = get_event_store()
        self.collection_name = collection_name

    async def publish(self, event: DomainEvent):
        await self.event_store.index(
            index=self.collection_name, id=event.order_id, body=event.dict()
        )