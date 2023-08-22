import json
from uuid import UUID, uuid4

from pydantic import Field

from domain.base.model import Model


class Entity(Model):
    """Base class for domain entitie objects."""

    id: UUID = Field(default_factory=uuid4)
    version: int = 0

    def increase_version(self):
        self.version += 1

    def to_dict(self):
        return json.loads(self.json())

    def __str__(self):
        return f'{type(self).__name__}'

    def __repr__(self):
        return self.__str__()


class AggregateRoot(Entity):
    """Base class for domain aggregate objects. Consits of 1+ entities"""
