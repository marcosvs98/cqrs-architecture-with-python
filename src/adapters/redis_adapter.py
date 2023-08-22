import json

import aioredis

from ports.cache_interface import CacheInterface
from settings import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT, REDIS_SSL


def silent_mode_wrapper(function):
    async def wrapper(*args, **kwargs):
        silent_mode = args[0].silent_mode
        if silent_mode:
            try:
                return await function(*args, **kwargs)
            except Exception as exc:
                return False
        else:
            return await function(*args, **kwargs)

    return wrapper


class RedisAdapter(CacheInterface):

    @staticmethod
    def __open_connection():
        redis_url = 'redis://'
        if REDIS_SSL:
            redis_url = 'rediss://'
        if REDIS_PASSWORD:
            redis_url += f':{REDIS_PASSWORD}@'

        redis_url += f'{REDIS_HOST}:{REDIS_PORT}/0'

        return aioredis.from_url(redis_url, decode_responses=True, encoding='utf8')  # noqa: E501

    @silent_mode_wrapper
    async def get(self, key: str):
        redis = self.__open_connection()
        return json.loads(await redis.get(key))

    @silent_mode_wrapper
    async def set(self, key: str, data: dict, ttl: int = 300):
        redis = self.__open_connection()
        await redis.set(key, json.dumps(data, default=str), ex=300)

    @silent_mode_wrapper
    async def delete(self, key: str):
        redis = self.__open_connection()
        await redis.delete(key)
