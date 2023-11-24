import motor.motor_asyncio
import pymongo

from domain.order.ports.store_connector_adapter_interface import StoreConnectorAdapterInterface


class MongoDBAdapterException(Exception):
    pass


class AsyncMongoDBConnectorAdapter(StoreConnectorAdapterInterface):
    def __init__(self, connection_str: str, database_name: str, server_timeout: int = 60000):
        self.connection_str = connection_str
        self.database_name = database_name
        self.server_timeout = server_timeout

    async def get_connection(self):
        client = motor.motor_asyncio.AsyncIOMotorClient(
            self.connection_str, serverSelectionTimeoutMS=self.server_timeout
        )
        try:
            # creating a reference to a database
            connection = client[self.database_name]
        except pymongo.errors.ServerSelectionTimeoutError as exc:
            raise MongoDBAdapterException(
                'Unable to connect to the server: server selection timeout'
            ) from exc
        except pymongo.errors.ConnectionFailure as exc:
            raise MongoDBAdapterException(
                'Unable to connect to the server: connection failure'
            ) from exc

        return connection
