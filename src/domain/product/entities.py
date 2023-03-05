from domain.model.entity import Entity
from domain.product.value_objects import ProductId


class Product(Entity):
    product_id: ProductId
    price: float
