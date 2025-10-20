from dependency_injector import containers, providers

import settings
from adapters.kafka_event_publisher import KafkaDomainEventPublisher
from adapters.mongo_db_connector_adapter import AsyncMongoDBConnectorAdapter
from adapters.redis_adapter import RedisAdapter
from domain.delivery.adapters.cost_calculator_adapter import (
    DeliveryCostCalculatorAdapter,
)
from domain.maps.adapters.google_maps_adapter import GoogleMapsAdapter
from domain.order.controllers.order_controller import OrderController
from domain.order.controllers.order_query_controller import OrderQueryController
from domain.order.repositories.order_event_store_repository import (
    OrderEventStoreRepository,
)
from domain.order.repositories.order_read_repository import OrderReadRepository
from domain.order.repositories.order_repository import (
    OrderRepository,
)
from domain.order.services.order_query_service import OrderQueryService
from domain.order.services.order_service import OrderService
from domain.payment.adapters.paypal_adapter import PayPalPaymentAdapter
from domain.product.adapters.product_adapter import ProductAdapter
from utils.logger import configure_logger

configure_logger()


class AppContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=[__name__])
    config = providers.Configuration()

    cache_adapter = providers.Singleton(RedisAdapter, silent_mode=settings.CACHE_SILENT_MODE)
    maps_adapter = providers.Singleton(GoogleMapsAdapter)
    payment_adapter = providers.Singleton(PayPalPaymentAdapter)
    product_adapter = providers.Singleton(ProductAdapter)
    delivery_cost_calculator = providers.Singleton(
        DeliveryCostCalculatorAdapter,
        maps_service=maps_adapter,
    )

    event_publisher = providers.Singleton(
        KafkaDomainEventPublisher,
        bootstrap_servers=settings.EVENT_PUBLISHER_KAFKA_BOOTSTRAP,
        topic=settings.EVENT_PUBLISHER_KAFKA_TOPIC,
        enabled=settings.EVENT_PUBLISHER_ENABLED,
    )

    order_event_store_connection = providers.Singleton(
        AsyncMongoDBConnectorAdapter,
        connection_str=settings.ORDER_EVENT_STORE_CONNECTION,
        database_name=settings.ORDER_EVENT_STORE_DATABASE_NAME,
    )

    order_repository_connection = providers.Singleton(
        AsyncMongoDBConnectorAdapter,
        connection_str=settings.ORDER_REPOSITORY_CONNECTION,
        database_name=settings.ORDER_REPOSITORY_DATABASE_NAME,
    )

    order_read_connection = providers.Singleton(
        AsyncMongoDBConnectorAdapter,
        connection_str=settings.ORDER_READ_CONNECTION,
        database_name=settings.ORDER_READ_DATABASE_NAME,
    )

    order_event_store_repository = providers.Singleton(
        OrderEventStoreRepository,
        db_connection=order_event_store_connection,
        collection_name=settings.ORDER_EVENT_STORE_COLLECTION_NAME,
    )

    order_repository = providers.Singleton(
        OrderRepository,
        cache_adapter=cache_adapter,
        db_connection=order_repository_connection,
        collection_name=settings.ORDER_REPOSITORY_COLLECTION_NAME,
    )

    order_read_repository = providers.Singleton(
        OrderReadRepository,
        cache_adapter=cache_adapter,
        db_connection=order_read_connection,
        collection_name=settings.ORDER_READ_COLLECTION_NAME,
    )

    order_service = providers.Factory(
        OrderService,
        repository=order_repository,
        payment_service=payment_adapter,
        product_service=product_adapter,
        delivery_service=delivery_cost_calculator,
        event_store=order_event_store_repository,
        read_repository=order_read_repository,
        event_publisher=event_publisher,
    )

    order_query_service = providers.Factory(
        OrderQueryService,
        read_repository=order_read_repository,
        event_store=order_event_store_repository,
    )

    order_controller = providers.Factory(OrderController, order_service=order_service)
    order_query_controller = providers.Factory(
        OrderQueryController,
        order_query_service=order_query_service,
    )
