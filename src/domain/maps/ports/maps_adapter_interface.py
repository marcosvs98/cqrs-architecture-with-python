import abc
from domain.maps.value_objects import Address


class MapsAdapterInterface(abc.ABC):
    @abc.abstractmethod
    async def calculate_distance_from_warehouses(self, destination: Address) -> float:
        raise NotImplementedError
