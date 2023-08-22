import abc


class StoreConnectorAdapterInterface(abc.ABC):
    @abc.abstractmethod
    async def get_connection(self):
        raise NotImplementedError
