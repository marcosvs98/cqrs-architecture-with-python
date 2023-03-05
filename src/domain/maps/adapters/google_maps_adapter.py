from domain.maps.ports.maps_adapter_interface import MapsAdapterInterface
from domain.maps.value_objects import Address


class GoogleMapsAdapter(MapsAdapterInterface):
    async def calculate_distance_from_warehouses(self, destination: Address) -> float:
        house_number = str(destination.house_number).split('/', maxsplit=1)[0]
        return float(house_number)
