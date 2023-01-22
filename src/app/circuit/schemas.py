from datetime import datetime
from ipaddress import IPv4Network, IPv6Network
from typing import List

from pydantic import AnyHttpUrl, EmailStr, root_validator

from src.app.base import BaseModel, BaseQuery
from src.app.circuit.const import CIRCUIT_STATUS
from src.utils.validators import items_to_list


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


class CircuitTypeBase(CircuitTypeCreate):
    id: int


class CircuitType(CircuitTypeBase):
    pass


class CircuitCreate(BaseModel):
    name: str
    description: str | None
    cid: str
    provider_id: int
    status: CIRCUIT_STATUS
    circuit_type_id: int
    provider_id: int
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
    contact_id: List[int] | None

    @root_validator(pre=False)
    def ip_trans(cls, values):
        if values["vender_available_ip"]:
            values["vender_available_ip"] = items_to_list(values["vender_available_ip"])
        if values["vender_available_gateway"]:
            values["vender_available_gateway"] = items_to_list(
                values["vender_available_gateway"]
            )
        return values


class CircuitUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    cid: str | None = None
    provider_id: int | None = None
    status: CIRCUIT_STATUS | None = None
    provider_id: int | None = None
    circuit_type_id: int | None = None
    install_date: datetime | None = None
    purchase_term: str | None = None
    commit_rate: int | None = None
    comments: str | None = None
    vender_available_ip: IPv4Network | List[IPv4Network] | None | IPv6Network | List[
        IPv6Network
    ] = None
    vender_available_gateway: IPv4Network | List[
        IPv4Network
    ] | None | IPv6Network | List[IPv6Network] = None
    contact_id: List[int] | None = None

    @root_validator(pre=False)
    def ip_trans(cls, values):
        if values["vender_available_ip"]:
            values["vender_available_ip"] = items_to_list(values["vender_available_ip"])
        if values["vender_available_gateway"]:
            values["vender_available_gateway"] = items_to_list(
                values["vender_available_gateway"]
            )
        return values


class CircuitBulkUpdate(BaseModel):
    ids: List[int]
    description: str | None = None
    status: CIRCUIT_STATUS | None = None
    provider_id: int | None = None
    circuit_type_id: int | None = None
    commit_rate: int | None = None
    contact_id: List[int] | None = None


class CircuitBulkDelete(BaseModel):
    ids: List[int]


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
