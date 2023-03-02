import abc
from domain.maps.value_objects import Address
from domain.maps.ports.maps_adapter_interface import MapsAdapterInterface


class DeliveryCostCalculatorAdapterInterface(abc.ABC):
    @abc.abstractmethod
    def __init__(self, maps_service: MapsAdapterInterface):
        raise NotImplementedError

    @abc.abstractmethod
    async def calculate_cost(self, total_product_cost: float, destination: Address) -> float:
        raise NotImplementedError

    @abc.abstractmethod
    async def _large_delivery_calculate_cost(self, destination: Address) -> float:
        raise NotImplementedError

    @abc.abstractmethod
    async def _small_delivery_calculate_cost(self, destination: Address) -> float:
        raise NotImplementedError
