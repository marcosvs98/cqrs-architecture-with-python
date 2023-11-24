from domain.base.entity import Entity
from domain.product.model.value_objects import ProductId


class Product(Entity):
    product_id: ProductId
    price: float
