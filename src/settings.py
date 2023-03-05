from decouple import config
from pydantic import BaseSettings

APPLICATION_NAME = config('APPLICATION_NAME', default='hexagonal-architecture-with-python')
PORT = config('PORT', default=8090, cast=int)
UVICORN_WORKERS = config('UVICORN_WORKERS', default=1, cast=int)

ELASTICSEARCH_ENDPOINT = config('ELASTICSEARCH_ENDPOINT', default='http://elasticsearch:9200')

REDIS_HOST = config("REDIS_HOST", default="redis")
REDIS_PORT = config("REDIS_PORT", default=6379, cast=int)
REDIS_PASSWORD = config("REDIS_PASSWORD", None)
REDIS_SSL = config("REDIS_SSL", default=False, cast=bool)
CACHE_SILENT_MODE = config("CACHE_SILENT_MODE", default=False, cast=bool)
