from src.api.base import BaseModel


class Endpoint(BaseModel):
    name: str
    url: str
    action: str
