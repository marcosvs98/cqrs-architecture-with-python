import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from utils.logger import get_logger

logger = get_logger()


class MongoDBAdapterException(Exception):
    """Exception raised for MongoDB adapter related errors."""


class AsyncMongoDBConnectorAdapter:
    def __init__(
        self,
        connection_str: str,
        database_name: str,
        server_timeout: int = 15_000,
        client: AsyncIOMotorClient | None = None,
    ):
        self.connection_str = connection_str
        self.database_name = database_name
        self.server_timeout = server_timeout
        self._client: AsyncIOMotorClient | None = client
        self._database: AsyncIOMotorDatabase | None = client[database_name] if client else None

    def _ensure_connection(self) -> None:
        if self._client is None:
            self._client = motor.motor_asyncio.AsyncIOMotorClient(
                self.connection_str,
                serverSelectionTimeoutMS=self.server_timeout,
                uuidRepresentation='standard',
            )
            self._database = self._client[self.database_name]

    async def _reset_connection(self) -> None:
        if self._client:
            await self._client.close()
        self._client = None
        self._database = None

    async def close(self) -> None:
        await self._reset_connection()

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[AsyncIOMotorDatabase]:
        try:
            self._ensure_connection()
            yield self._database
        except (ServerSelectionTimeoutError, ConnectionFailure) as exc:
            await logger.exception('MongoDB connection failed')
            await self._reset_connection()
            raise MongoDBAdapterException(
                f'MongoDB connection failed for {self.database_name} and has been reset.'
            ) from exc

    def __del__(self) -> None:
        if self._client:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.close())
            except RuntimeError:
                pass
