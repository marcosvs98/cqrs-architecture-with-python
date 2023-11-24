import asyncio

from aiokafka import AIOKafkaProducer

from domain.base.event import DomainEvent
from domain.order.ports.event_publisher_interface import EventPublisherInterface


class KafkaEventPublisher(EventPublisherInterface):
    def __init__(self, config: dict):
        self.config = config
        self.producer = None

    async def _initialize_producer(self):
        if self.producer is None:
            self.producer = AIOKafkaProducer(loop=asyncio.get_event_loop(), **self.config)
            await self.producer.start()

    async def publish_event(self, event: DomainEvent):
        await self._initialize_producer()
        await self.producer.send_and_wait(event.event_name, event.json().encode('utf-8'))

    async def close(self):
        if self.producer is not None:
            await self.producer.stop()
            self.producer = None
