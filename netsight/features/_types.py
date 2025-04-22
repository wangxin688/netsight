from datetime import datetime
from enum import Enum
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
from typing import Annotated, Generic, Literal, ParamSpec, TypeVar

import pydantic
from fastapi import Query
from pydantic import ConfigDict, Field, StringConstraints
from pydantic.functional_validators import BeforeValidator

from netsight.core.utils.validators import items_to_list, mac_address_validator

T = TypeVar("T")
P = ParamSpec("P")
R = TypeVar("R")

type Order = Literal["descend", "ascend"]

StrList = Annotated[str | list[str], BeforeValidator(items_to_list)]
IntList = Annotated[int | list[int], BeforeValidator(items_to_list)]
MacAddress = Annotated[str, BeforeValidator(mac_address_validator)]
NameStr = Annotated[str, StringConstraints(pattern="^[a-zA-Z0-9_-].$", max_length=50)]
NameChineseStr = Annotated[str, StringConstraints(pattern="^[\u4e00-\u9fa5a-zA-Z0-9_-].$", max_length=50)]

type IPvAnyInterface = IPv4Interface | IPv6Interface
type IPvAnyAddress = IPv4Address | IPv6Address
type IPvAnyNetwork = IPv4Network | IPv6Network


class BaseModel(pydantic.BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AuditTime(BaseModel):
    created_at: datetime
    updated_at: datetime | None = None


class AuthUserBase(BaseModel):
    id: int
    name: str
    email: str | None = None
    avatar: str | None = None


class AuditUser(AuditTime):
    created_by: AuthUserBase | None = None
    updated_by: AuthUserBase | None = None


class AuditLog(BaseModel):
    id: int
    created_at: datetime
    request_id: str
    action: str
    diff: dict | None = None
    user: AuthUserBase | None = None


class ListT(BaseModel, Generic[T]):
    count: int
    results: list[T] | None = None


class AppStrEnum(str, Enum):
    def __str__(self) -> str:
        return str.__str__(self)

    @classmethod
    def to_list(cls) -> list[str]:
        return [c.value for c in cls]


class AuditTimeQuery(BaseModel):
    created_at__lte: datetime
    created_at__gte: datetime
    updated_at__lte: datetime
    updated_at__gte: datetime


class AuidtUserQuery(BaseModel):
    created_by_fk: list[int] = Field(Query(default=[]))
    updated_by_fk: list[int] = Field(Query(default=[]))


class QueryParams(BaseModel):
    limit: int | None = Query(default=20, ge=0, le=1000, description="Number of results to return per request.")
    offset: int | None = Query(default=0, ge=0, description="The initial index from which return the results.")
    q: str | None = Query(default=None, description="Search for results.")
    id: list[int] | None = Field(Query(default=[], description="request object unique ID"))
    order_by: str | None = Query(default=None, description="Which field to use when order the results")
    order: Order | None = Query(default="ascend", description="Order by dscend or ascend")


class BatchDelete(BaseModel):
    ids: list[int]


class BatchUpdate(BaseModel):
    ids: list[int]


class I18nField(BaseModel):
    en: str
    zh: str


class IdResponse(BaseModel):
    id: int
