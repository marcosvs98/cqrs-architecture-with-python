from domain.base.event import DomainEvent
from domain.base.ports.event_adapter_interface import DomainEventPublisher
from domain.order.ports.event_publisher_interface import \
    EventPublisherInterface
from domain.order.ports.order_event_store_repository_interface import \
    OrderEventStoreRepositoryInterface


class OrderEventPublisher(DomainEventPublisher):
    def __init__(
        self,
        repository: OrderEventStoreRepositoryInterface,
        publisher: EventPublisherInterface,
    ):
        self.repository = repository
        self.publisher = publisher

    async def publish(self, event: DomainEvent) -> None:
        await self.repository.save(event)
        await self.publisher.publish_event(event)
