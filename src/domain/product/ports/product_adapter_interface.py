import abc

from domain.product.model.value_objects import ProductId


class ProductAdapterInterface(abc.ABC):
    @abc.abstractmethod
    async def total_price(self, product_counts: list[tuple[ProductId, int]]) -> float:
        raise NotImplementedError
