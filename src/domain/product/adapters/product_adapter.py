from domain.product.model.value_objects import ProductId
from domain.product.ports.product_adapter_interface import ProductAdapterInterface


class ProductAdapter(ProductAdapterInterface):
    async def total_price(self, product_counts: list[tuple[ProductId, int]]) -> float:
        price_list = [12.0 * count for product, count in product_counts]
        return float(sum(price_list))
