from pydantic import ConfigDict

from domain.base.model import Model


class DataTransferObject(Model):
    """Base class for data transfer objects (DTOs)"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DataTransferObject):
            return False

        for field_name in self.__fields__:
            if getattr(self, field_name) != getattr(other, field_name):
                return False
        return True
