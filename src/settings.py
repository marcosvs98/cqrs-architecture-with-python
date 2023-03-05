from decouple import config
from pydantic import BaseSettings

APPLICATION_NAME = config('APPLICATION_NAME', default='hexagonal-architecture-with-python')
PORT = config('PORT', default=8000, cast=int)
UVICORN_WORKERS = config('UVICORN_WORKERS', default=1, cast=int)

ELASTICSEARCH_ENDPOINT = config('ELASTICSEARCH_ENDPOINT', default='http://elasticsearch:9200')
