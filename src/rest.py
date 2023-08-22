from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import settings
from adapters.redis_adapter import RedisAdapter
from domain.delivery.adapters.cost_calculator_adapter import (
    DeliveryCostCalculatorAdapter,
)
from domain.maps.adapters.google_maps_adapter import GoogleMapsAdapter
from domain.order.adapters.kafka_publisher_adapter import KafkaEventPublisher
from domain.order.adapters.mongo_db_connector_adapter import (
    AsyncMongoDBConnectorAdapter,
)
from domain.order.adapters.order_event_publisher_adapter import (
    OrderEventPublisher,
)
from domain.order.controllers.order_controller import OrderController
from domain.order.repository.order_aggregate_repository import (
    OrderAggregateRepository,
)
from domain.order.repository.order_event_store_repository import (
    OrderEventStoreRepository,
)
from domain.order.repository.order_persistence_repository import (
    OrderPersistenceRepository,
)
from domain.order.services.order_command import OrderCommand
from domain.order.services.order_mediator import OrderMediator
from domain.order.services.order_query import OrderQuery
from domain.payment.adapters.paypal_adapter import PayPalPaymentAdapter
from domain.product.adapters.product_adapter import ProductAdapter
from exceptions import CommonException
from schemas import HealthCheck


def init_middlewares(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=False,
        allow_methods=['*'],
        allow_headers=['*'],
    )


def init_routes(app: FastAPI):
    @app.get('/', status_code=200, response_model=HealthCheck)
    async def health_check():
        return {'status': 200}

    event_publisher = OrderEventPublisher(
        repository=OrderEventStoreRepository(
            db_connection=AsyncMongoDBConnectorAdapter(
                connection_str=settings.ORDER_EVENT_STORE_CONNECTION,
                database_name=settings.ORDER_EVENT_STORE_DATABASE_NAME,
            ),
            collection_name=settings.ORDER_EVENT_STORE_COLLECTION_NAME,
        ),
        publisher=KafkaEventPublisher(config=settings.KAFKA_SETTINGS)
    )

    app.include_router(
        OrderController(
            OrderMediator(
                command=OrderCommand(
                    repository=OrderAggregateRepository(
                        db_connection=AsyncMongoDBConnectorAdapter(
                            connection_str=settings.ORDER_REPOSITORY_CONNECTION,
                            database_name=settings.ORDER_REPOSITORY_DATABASE_NAME,
                        ),
                        collection_name=settings.ORDER_REPOSITORY_COLLECTION_NAME,
                    ),
                    payment_service=PayPalPaymentAdapter(),
                    product_service=ProductAdapter(),
                    delivery_service=DeliveryCostCalculatorAdapter(maps_service=GoogleMapsAdapter()),
                    event_publisher=event_publisher
                ),
                query=OrderQuery(
                    repository=OrderAggregateRepository(
                        db_connection=AsyncMongoDBConnectorAdapter(
                            connection_str=settings.ORDER_REPOSITORY_CONNECTION,
                            database_name=settings.ORDER_REPOSITORY_DATABASE_NAME,
                        ),
                        collection_name=settings.ORDER_REPOSITORY_COLLECTION_NAME,
                    )
                ),
                cache_repository=OrderPersistenceRepository(
                    cache_adapter=RedisAdapter(silent_mode=settings.CACHE_SILENT_MODE)
                )
            )
        ).router,
        tags=['order'],
        prefix='/api/v1/order',
    )

    @app.exception_handler(CommonException)
    async def service_exception_handler(request: Request, error: CommonException):
        return JSONResponse(error.to_dict(), status_code=error.code)
