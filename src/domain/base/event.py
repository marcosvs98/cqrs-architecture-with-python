from datetime import datetime as dt
from uuid import UUID, uuid4

from pydantic import Field

from domain.base.entity import AggregateRoot, Entity


class DomainEvent(Entity):
    """Base class for domain events objects"""

    event_name: str
    tracker_id: UUID = Field(default_factory=uuid4)
    datetime: dt = Field(default_factory=dt.now)
    aggregate: AggregateRoot

    @classmethod
    def domain_event_name(cls):
        return cls.__name__

    def __eq__(self, other: 'DomainEvent'):
        if type(self) is not type(other):
            return False
        return self.serialize() == other.serialize()

    class Config:
        arbitrary_types_allowed = True
