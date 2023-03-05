from domain.base.model import Model


class DomainEvent(Model):
    """Base class for domain events objects"""

    @classmethod
    def domain_event_name(cls):
        return cls.__name__

    def __eq__(self, other: 'DomainEvent'):
        if type(self) is not type(other):
            return False
        return self.serialize() == other.serialize()

    class Config:
        arbitrary_types_allowed = True
