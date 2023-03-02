from pydantic import BaseModel


class HealthCheck(BaseModel):
    status: int
