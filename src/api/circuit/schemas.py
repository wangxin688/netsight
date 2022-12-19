from datetime import datetime
from ipaddress import IPv4Network, IPv6Network
from typing import List

from pydantic import AnyHttpUrl, EmailStr

from src.api.base import BaseModel, BaseQuery


class Provider(BaseModel):
    id: int
    name: str
    description: str | None
    asn: int | None
    account: str | None
    portal: AnyHttpUrl | None
    noc_contact: List[EmailStr] | None
    admin_contact: List[EmailStr] | None
    comments: str | None
    # circuit: List[CircuitBase] | None

    class Config:
        orm_mode = True


class ProviderBase(BaseModel):
    id: int
    name: str
    description: str | None
    asn: int | None
    account: str | None
    portal: AnyHttpUrl | None
    noc_contact: List[EmailStr] | None
    admin_contact: List[EmailStr] | None
    comments: str | None

    class Config:
        orm_mode = True


class CircuitType(BaseModel):
    id: int
    name: str
    description: str | None
    # dcim_circuit: List[CircuitBase] | None

    class Config:
        orm_mode = True


class CircuitTypeBase(BaseModel):
    id: int
    name: str
    description: str | None

    class Config:
        orm_mode = True


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


class CircuitTypeCreate(BaseModel):
    name: str
    description: str | None


class CricuitTypeUpdate(BaseModel):
    name: str | None
    description: str | None


()


class CircuitTypeQuery(BaseQuery):
    pass


class CircuitCreate(BaseModel):
    name: str
    description: str | None


class CricuitUpdate(BaseModel):
    name: str | None
    description: str | None


()


class CircuitQuery(BaseQuery):
    pass


class ProviderCreate(BaseModel):
    name: str
    description: str | None
    asn: int | None
    account: str | None
    portal: AnyHttpUrl | None
    noc_contact: List[EmailStr] | None
    admin_contact: List[EmailStr] | None
    comments: str | None


class ProviderUpdate(BaseModel):
    name: str | None
    description: str | None
    asn: int | None
    account: str | None
    portal: AnyHttpUrl | None
    noc_contact: List[EmailStr] | None
    admin_contact: List[EmailStr] | None
    comments: str | None


()


class ProviderQuery(BaseQuery):
    pass
