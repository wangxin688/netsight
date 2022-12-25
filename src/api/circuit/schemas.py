from datetime import datetime
from ipaddress import IPv4Network, IPv6Network
from typing import List

from pydantic import AnyHttpUrl, EmailStr

from src.api.base import BaseModel, BaseQuery


class ProviderCreate(BaseModel):
    name: str
    description: str | None
    asn: int | None
    account: str | None
    portal: AnyHttpUrl | None
    noc_contact: List[EmailStr] | None
    admin_contact: List[EmailStr] | None
    comments: str | None


class ProviderQuery(BaseQuery):
    pass


class ProviderUpdate(ProviderCreate):
    name: str | None


class ProviderBulkUpdate(BaseModel):
    ids: List[int]
    description: str | None
    asn: int | None
    account: str | None
    portal: AnyHttpUrl | None
    noc_contact: List[EmailStr] | None
    admin_contact: List[EmailStr] | None
    comments: str | None


class ProviderBulkDelete(BaseModel):
    ids: List[int]


class ProviderBase(ProviderCreate):
    id: int


class Provider(ProviderBase):
    pass


class CircuitTypeCreate(BaseModel):
    name: str
    description: str | None


class CircuitTypeQuery(BaseQuery):
    pass


class CircuitTypeUpdate(BaseModel):
    name: str | None
    description: str | None


class CircuitTypeBulkDelete(BaseModel):
    ids: List[int]


class CricuitTypeUpdate(BaseModel):
    name: str | None
    description: str | None


class CircuitTypeBase(CircuitTypeCreate):
    id: int


class CircuitType(CircuitTypeBase):
    pass


class CircuitCreate(BaseModel):
    name: str
    description: str | None
    cid: str
    provider_id: int
    status: str
    circuit_type_id: int
    install_date: datetime | None
    purchase_term: str
    commit_rate: int | None
    comments: str | None
    vender_available_ip: IPv4Network | List[IPv4Network] | IPv6Network | List[
        IPv6Network
    ] | None
    vender_available_gateway: IPv4Network | List[IPv4Network] | IPv6Network | List[
        IPv6Network
    ] | None
    contact_id: int | None


class CricuitUpdate(BaseModel):
    name: str | None
    description: str | None
    cid: str | None
    provider_id: int
    status: str | None
    circuit_type_id: int | None
    install_date: datetime | None
    purchase_term: str | None
    commit_rate: int | None
    comments: str | None
    vender_available_ip: IPv4Network | List[IPv4Network] | None | IPv6Network | List[
        IPv6Network
    ]
    vender_available_gateway: IPv4Network | List[
        IPv4Network
    ] | None | IPv6Network | List[IPv6Network]
    contact_id: int | None


class CircuitQuery(BaseQuery):
    pass


class Circuit(BaseModel):
    id: int
    name: str
    description: str | None
    cid: str
    circuit_provider: Provider
    status: str
    circuit_type: CircuitTypeBase
    install_date: datetime | None
    purchase_term: str
    commit_rate: int | None
    comments: str | None
    vender_available_ip: IPv4Network | List[IPv4Network] | None | IPv6Network | List[
        IPv6Network
    ] | None
    vender_available_gateway: IPv4Network | List[
        IPv4Network
    ] | None | IPv6Network | List[IPv6Network] | None
    # contact: List[ContactBase] | None
    # circuit_termination: List[CircuitTerminationBase] | None

    class Config:
        orm_mode = True


class CircuitBase(BaseModel):
    id: int
    name: str
    description: str | None
    cid: str
    circuit_provider: Provider
    status: str
    circuit_type: CircuitTypeBase
    install_date: datetime | None
    purchase_term: str
    commit_rate: int | None
    comments: str | None
    vender_available_ip: IPv4Network | List[IPv4Network] | None | IPv6Network | List[
        IPv6Network
    ] | None
    vender_available_gateway: IPv4Network | List[
        IPv4Network
    ] | None | IPv6Network | List[IPv6Network] | None

    class Config:
        orm_mode = True
