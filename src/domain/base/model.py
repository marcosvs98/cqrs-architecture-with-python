from pydantic import BaseModel, ConfigDict


class Model(BaseModel):
    """Base class for model objects"""

    model_config = ConfigDict(extra='allow')
