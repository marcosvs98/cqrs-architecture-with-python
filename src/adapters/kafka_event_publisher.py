from __future__ import annotations

import asyncio
import json

from aiokafka import AIOKafkaProducer

from domain.base.event import DomainEvent
from domain.base.ports.event_adapter_interface import DomainEventPublisher
from utils.logger import get_logger

logger = get_logger(__name__)


class KafkaDomainEventPublisher(DomainEventPublisher):
    """Kafka-backed domain event publisher."""

    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
        enabled: bool = True,
    ) -> None:
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.enabled = enabled and bool(bootstrap_servers and topic)
        self._producer: AIOKafkaProducer | None = None
        self._lock = asyncio.Lock()

    async def publish(self, event: DomainEvent) -> None:
        if not self.enabled:
            await logger.debug('Event publisher disabled', event_name=event.event_name)
            return

        try:
            producer = await self._ensure_producer()
        except Exception as exc:  # pragma: no cover - defensive path
            await logger.exception(
                'Failed to initialise Kafka producer',
                event_name=event.event_name,
                error=str(exc),
            )
            return

        payload = event.model_dump(mode='json')
        try:
            await producer.send_and_wait(self.topic, payload)
            await logger.info(
                'Event published to Kafka',
                topic=self.topic,
                event_name=event.event_name,
                tracker_id=str(event.tracker_id),
            )
        except Exception as exc:  # pragma: no cover - network failure
            await logger.exception(
                'Failed to publish event to Kafka',
                topic=self.topic,
                event_name=event.event_name,
                error=str(exc),
            )

    async def close(self) -> None:
        if self._producer is not None:
            await self._producer.stop()
            self._producer = None

    async def _ensure_producer(self) -> AIOKafkaProducer:
        if self._producer is not None:
            return self._producer

        async with self._lock:
            if self._producer is None:
                producer = AIOKafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    value_serializer=lambda value: json.dumps(value).encode('utf-8'),
                )
                await producer.start()
                self._producer = producer
        return self._producer
