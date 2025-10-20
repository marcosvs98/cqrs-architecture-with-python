from collections.abc import Sequence
from decimal import Decimal

from domain.product.model.value_objects import ProductId
from domain.product.ports.product_adapter_interface import ProductAdapterInterface


class ProductAdapter(ProductAdapterInterface):
    """Mock product adapter for calculating total price."""

    async def total_price(self, product_counts: Sequence[tuple[ProductId, int]]) -> Decimal:
        """Return total price given a sequence of product/count tuples."""
        unit_price = Decimal('12')
        return sum(unit_price * Decimal(count) for _, count in product_counts)
