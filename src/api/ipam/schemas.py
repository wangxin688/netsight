from datetime import datetime
from ipaddress import IPv4Network, IPv6Network

from src.api.base import BaseModel


class RIR(BaseModel):
    id: int
    name: str
    description: str | None
    is_private: bool
    created_at: datetime
    updated_at: datetime | None
    # ipam_block: List[Block] | None

    class Config:
        orm_mode = True


class RIRBase(BaseModel):
    id: int
    name: str
    description: str | None
    is_private: bool
    created_at: datetime
    updated_at: datetime | None

    class Config:
        orm_mode = True


class RIRCreate(BaseModel):
    name: IPv4Network | IPv6Network
    description: str | None
    is_private: bool


class RIRUpdate(BaseModel):
    name: IPv4Network | IPv6Network | None
    description: str | None
    is_private: bool | None
