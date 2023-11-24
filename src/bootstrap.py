import settings
from adapters.redis_adapter import RedisAdapter
from domain.delivery.adapters.cost_calculator_adapter import DeliveryCostCalculatorAdapter
from domain.maps.adapters.google_maps_adapter import GoogleMapsAdapter
from domain.order.adapters.kafka_publisher_adapter import KafkaEventPublisher
from domain.order.adapters.mongo_db_connector_adapter import AsyncMongoDBConnectorAdapter
from domain.order.adapters.order_event_publisher_adapter import OrderEventPublisher
from domain.order.controllers.order_controller import OrderController
from domain.order.repositories.order_aggregate_cache_repository import OrderAggregateCacheRepository
from domain.order.repositories.order_aggregate_repository import OrderAggregateRepository
from domain.order.repositories.order_event_store_repository import OrderEventStoreRepository
from domain.order.services.order_command import OrderCommand
from domain.order.services.order_mediator import OrderMediator
from domain.order.services.order_query import OrderQuery
from domain.payment.adapters.paypal_adapter import PayPalPaymentAdapter
from domain.product.adapters.product_adapter import ProductAdapter


def initialize_order_controller():
    # Initialize MongoDB connection for Order Event Store
    order_event_store_repository = OrderEventStoreRepository(
        db_connection=AsyncMongoDBConnectorAdapter(
            connection_str=settings.ORDER_EVENT_STORE_CONNECTION,
            database_name=settings.ORDER_EVENT_STORE_DATABASE_NAME,
        ),
        collection_name=settings.ORDER_EVENT_STORE_COLLECTION_NAME,
    )

    # Initialize Kafka Event Publisher
    kafka_event_publisher = KafkaEventPublisher(config=settings.KAFKA_SETTINGS)

    # Initialize Order Event Publisher
    event_publisher = OrderEventPublisher(
        repository=order_event_store_repository, publisher=kafka_event_publisher
    )

    # Initialize MongoDB connection for Order Repository
    order_repository = OrderAggregateRepository(
        db_connection=AsyncMongoDBConnectorAdapter(
            connection_str=settings.ORDER_REPOSITORY_CONNECTION,
            database_name=settings.ORDER_REPOSITORY_DATABASE_NAME,
        ),
        collection_name=settings.ORDER_REPOSITORY_COLLECTION_NAME,
    )

    # Initialize Redis Cache Adapter
    redis_cache_adapter = RedisAdapter(silent_mode=settings.CACHE_SILENT_MODE)

    # Initialize Order Cache Repository
    cache_repository = OrderAggregateCacheRepository(cache_adapter=redis_cache_adapter)

    # Initialize Google Maps Adapter for Delivery Cost Calculator
    delivery_cost_calculator_adapter = DeliveryCostCalculatorAdapter(
        maps_service=GoogleMapsAdapter()
    )

    # Initialize Order Command Service
    order_command = OrderCommand(
        repository=order_repository,
        payment_service=PayPalPaymentAdapter(),
        product_service=ProductAdapter(),
        delivery_service=delivery_cost_calculator_adapter,
        event_publisher=event_publisher,
    )

    # Initialize Order Query Service
    order_query = OrderQuery(repository=order_repository)

    # Initialize Order Mediator
    order_mediator = OrderMediator(
        command=order_command, query=order_query, cache_repository=cache_repository
    )

    # Initialize Order Controller
    order_controller = OrderController(order_mediator)

    return order_controller
