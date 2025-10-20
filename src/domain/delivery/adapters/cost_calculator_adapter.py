from decimal import Decimal

from domain.delivery.ports.cost_calculator_interface import DeliveryCostCalculatorAdapterInterface
from domain.maps.model.value_objects import Address
from domain.maps.ports.maps_adapter_interface import MapsAdapterInterface

ORDER_PRICE_THRESHOLD = Decimal('500')
FREE_DISTANCE_THRESHOLD = Decimal('30')
FREE = Decimal('0')
FLAT_PRICE = Decimal('50')
BASE_PRICE = Decimal('50')
PRICE_PER_EXTRA_DISTANCE = Decimal('15')


class DeliveryCostCalculatorAdapter(DeliveryCostCalculatorAdapterInterface):
    """Delivery cost calculator using distance and product cost thresholds."""

    def __init__(self, maps_service: MapsAdapterInterface) -> None:
        self.maps_service = maps_service

    async def calculate_cost(self, total_product_cost: Decimal, destination: Address) -> Decimal:
        """Decide whether to calculate cost as a large or small delivery."""
        if total_product_cost >= ORDER_PRICE_THRESHOLD:
            return await self._large_delivery_calculate_cost(destination)
        return await self._small_delivery_calculate_cost(destination)

    async def _large_delivery_calculate_cost(self, destination: Address) -> Decimal:
        """Calculate delivery cost for large orders."""
        distance = await self.maps_service.calculate_distance_from_warehouses(destination)
        if Decimal(distance) <= FREE_DISTANCE_THRESHOLD:
            return FREE
        return FLAT_PRICE

    async def _small_delivery_calculate_cost(self, destination: Address) -> Decimal:
        """Calculate delivery cost for small orders."""
        distance = await self.maps_service.calculate_distance_from_warehouses(destination)
        if Decimal(distance) <= FREE_DISTANCE_THRESHOLD:
            return BASE_PRICE

        distance_extra = Decimal(distance) - FREE_DISTANCE_THRESHOLD
        return BASE_PRICE + PRICE_PER_EXTRA_DISTANCE * distance_extra
