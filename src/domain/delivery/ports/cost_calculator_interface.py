import abc
from decimal import Decimal

from domain.maps.model.value_objects import Address
from domain.maps.ports.maps_adapter_interface import MapsAdapterInterface


class DeliveryCostCalculatorAdapterInterface(abc.ABC):
    """Abstraction for calculating delivery costs based on destination and product value."""

    def __init__(self, maps_service: MapsAdapterInterface) -> None:
        self.maps_service = maps_service

    @abc.abstractmethod
    async def calculate_cost(self, total_product_cost: Decimal, destination: Address) -> Decimal:
        """Calculate the delivery cost based on product cost and destination."""
        raise NotImplementedError

    @abc.abstractmethod
    async def _large_delivery_calculate_cost(self, destination: Address) -> Decimal:
        """Specialized calculation for large deliveries."""
        raise NotImplementedError()

    @abc.abstractmethod
    async def _small_delivery_calculate_cost(self, destination: Address) -> Decimal:
        """Specialized calculation for small deliveries."""
        raise NotImplementedError()
