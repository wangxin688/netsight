from typing import Set

from pydantic import validator

from app.auth.const import METHOD
from src.app.base import BaseModel


class Endpoint(BaseModel):
    name: str
    url: str
    action: Set[str]

    @validator("action")
    def action_validator(cls, v):
        return list(METHOD & v)[0]
