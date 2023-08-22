from decouple import config
from pydantic import BaseSettings

APPLICATION_NAME = config('APPLICATION_NAME', default='hexagonal-architecture-with-python')
PORT = config('PORT', default=8090, cast=int)
UVICORN_WORKERS = config('UVICORN_WORKERS', default=1, cast=int)


REDIS_HOST = config('REDIS_HOST', default='redis')
REDIS_PORT = config('REDIS_PORT', default=6379, cast=int)
REDIS_PASSWORD = config('REDIS_PASSWORD', None)
REDIS_SSL = config('REDIS_SSL', default=False, cast=bool)
CACHE_SILENT_MODE = config('CACHE_SILENT_MODE', default=False, cast=bool)


ORDER_REPOSITORY_CONNECTION = config(
    'ORDER_REPOSITORY_CONNECTION',
    default='mongodb://admin:root@order-aggregate-repository_mongo-db:27017/'
)
ORDER_REPOSITORY_DATABASE_NAME = config(
    'ORDER_REPOSITORY_DATABASE_NAME', default='order_aggregates'
)
ORDER_REPOSITORY_COLLECTION_NAME = config(
    'ORDER_REPOSITORY_COLLECTION_NAME', default='order_aggregates'
)

ORDER_EVENT_STORE_CONNECTION = config(
    'ORDER_EVENT_STORE_CONNECTION',
    default='mongodb://admin:root@order-event-store-repository_mongo-db:27017/'
)
ORDER_EVENT_STORE_DATABASE_NAME = config(
    'ORDER_EVENT_STORE_DATABASE_NAME', default='order_events'
)
ORDER_EVENT_STORE_COLLECTION_NAME = config(
    'ORDER_EVENT_STORE_COLLECTION_NAME', default='order_events'
)

KAFKA_SETTINGS = {"bootstrap_servers": "kafka:9092"}