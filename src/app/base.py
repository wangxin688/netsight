"""Base class定义逻辑关系自顶向下, site->location->rack->device-interface, 关系设计不能反向
   Base class定义顺序自下向顶, 层级最高定义位置在最后
"""
from datetime import datetime
from typing import Generic, NamedTuple, Optional, TypeVar

import pydantic
from pydantic.generics import GenericModel


def default(obj):
    if isinstance(obj, datetime):
        return int(obj.timestamp())


class BaseModel(pydantic.BaseModel):
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: int(v.timestamp())
        }  # method for customer JSON encoding of datetime fields


DataT = TypeVar("DataT", bound=BaseModel)


class BaseResponse(GenericModel, Generic[DataT]):
    code: int
    data: Optional[DataT] = None
    msg: str

    class Config:
        json_encoders = {
            datetime: lambda v: int(v.timestamp())
        }  # method for customer JSON encoding of datetime fields


class ListData(GenericModel, Generic[DataT]):
    count: int
    results: Optional[DataT]


class BaseListResponse(GenericModel, Generic[DataT]):
    code: int
    data: ListData
    msg: str

    class Config:
        json_encoders = {
            datetime: lambda v: int(v.timestamp())
        }  # method for customer JSON encoding of datetime fields


class QueryParams(NamedTuple):
    limit: int | None = 20
    offset: int | None = 0


class BaseQuery(BaseModel):
    limit: int = 20
    offset: int | None = 0
    q: str | None = None
