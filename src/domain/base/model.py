from pydantic import BaseModel, Extra


class Model(BaseModel, extra=Extra.allow):
    """Base class for model objects"""
