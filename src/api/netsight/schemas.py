from typing import Set

from pydantic import validator

from src.api.auth.constraints import METHOD
from src.api.base import BaseModel


class Endpoint(BaseModel):
    name: str
    url: str
    action: Set[str]

    @validator("action")
    def action_validator(cls, v):
        return list(METHOD & v)[0]
