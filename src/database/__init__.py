import motor.motor_asyncio
from settings import MongoDatabaseSettings


def get_mongo_db(config: MongoDatabaseSettings):
    uri = f'mongodb://{config.MONGO_USERNAME}:{config.MONGO_PASSWORD}@{config.MONGO_SERVER}:{config.MONGO_PORT}'  # noqa: E501
    client = motor.motor_asyncio.AsyncIOMotorClient(uri)
    db = client.OrderingService
    return db
