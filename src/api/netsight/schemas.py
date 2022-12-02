from typing import List

from src.api.base import BaseModel


class Endpoint(BaseModel):
    name: str
    url: str
    action: List[str]
