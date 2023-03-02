from decouple import config
from pydantic import BaseSettings

APPLICATION_NAME = config('APPLICATION_NAME', default='hexagonal-architecture-with-python')
PORT = config('PORT', default=8090, cast=int)
UVICORN_WORKERS = config('UVICORN_WORKERS', default=3, cast=int)


class MongoDatabaseSettings(BaseSettings):
    MONGO_SERVER: str = 'mongo-db'
    MONGO_PORT: str = '27017'
    MONGO_USERNAME: str = ''
    MONGO_PASSWORD: str = ''
